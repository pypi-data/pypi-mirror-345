# See LICENSE.md file in project root directory

import os
import json
import shutil
import signal
import logging
import traceback
from queue import Queue
from datetime import datetime
from retry_requests import retry, RSession
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener

from .Stax import Stax

sess = retry(RSession(timeout=30), retries=3)

def log(*args):
    print("[" + str(datetime.now()) + "]", *args)

def result(obj):
    with open('response.json', 'w') as f:
        json.dump(obj, f)

def setup_logger(): #
    """
    Central Logger Configuration
    Setup handler, formatter, and queue for logging.
    """
    log_queue = Queue()

    # File handler with rotation - this is to prevent logs from growing indefinitely
    file_handler = RotatingFileHandler('job.log', maxBytes=1e7, backupCount=0)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    file_handler.setFormatter(file_formatter)

    # Console handler for real-time logs - useful for debugging and having the logs on the terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    console_handler.setFormatter(console_formatter)

    # Queue handler for asynchronous logging - this is to prevent blocking 
    queue_handler = QueueHandler(log_queue)

    # Root logger configuration - this is the main logger that will be used
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(queue_handler)

    # Listener thread for processing logs from the queue - this is to prevent blocking
    listener = QueueListener(log_queue, file_handler, console_handler)
    listener.start()

    return root_logger, listener

# Initialize Logger Globally 
logger, log_listener = setup_logger()

# Define module wrapper decorator
def def_module(module_id:str, module_key:str):
    def wrapper(app):
        def inner(*args, **kwargs):

            starttime = datetime.utcnow()
            TEST = "test" in kwargs and kwargs["test"]
            logger.info("Starting Stax.ai module:", module_id)  

            # Setup keyboard interrupt handler (if worker is killed)
            signal.signal(signal.SIGINT, signal.default_int_handler)

            # Load request.json file
            if not os.path.exists('request.json'):
                raise Exception("Missing request.json file.")

            with open('request.json') as f:
                req = json.load(f)

            try:
                job:str = req["jobId"]
                team:str = req["teamId"]
                document:str = req["documentId"]
                stack:str = req["stackId"]
                step:str = req["stepId"]
                stepN:str = req["step"]
                config:list[dict] = req["config"]

            except:
                raise Exception("Missing required fields in request.json.")

            # Step identifier to report status to the Stax.ai API
            report = {
                "step": stepN,
                "stepId": step,
                "stack": stack,
            }

            # Instantiate a Stax.ai API object
            stax = Stax(
                module_id=module_id,
                module_key=module_key,
                team_id=team,
                document=document,
                api_url=os.getenv('STAX_API_URL', default='https://api.stax.ai')
            )

            try:
                # before we even try to do anything else, let's try to set the startTime value in the job object in the DB.
                # we will send a stax api request over to the job/start endpoint. If the job already is running or
                # completed already then it will return a 429 error, if not it will be 200 and we can continue on 
                # with the code. 
                if not TEST:
                    try:
                        # note that job_start_res isn't used anywhere but we'll keep it here for debugging purposes.
                        stax.post('/job/start/', {"jobId": job})
    
                    except Exception as e:
                        if '429' in str(e):
                            log("Job not found or job is running / completed for job ID:", job)
                            exit()

                logger.info("Started job:", job)
                
                # Call module/app function
                count = app(stax, document, stack, team, config)

                # Finished job, post result to Stax.ai API
                result({ "status": "Complete", "units": count })
                if not TEST:
                    stax.post('/job/complete/' + job, {
                        **report,
                        "count": count
                    })

                logger.info("Completed job:", job)  

            except KeyboardInterrupt:
                log("SIGINT Received. Stopping job:", job)
                result({ "status": "Killed" })

                # Let the Stax.ai API know what happened so it can handle it
                if not TEST:
                    stax.post('/job/complete/' + job, {
                        **report,
                        "error": "Automate module worker was stopped. This job should be retried shortly."
                    })

                exit()

            except Exception as e:
                trace = traceback.format_exc()
                logger.error("Error in job:", job)

                error = {
                    "error": str(e),
                    "traceback": str(trace)
                }
                result({ "status": "Error", **error })

                # Report error to the Stax.ai API
                if not TEST:
                    stax.post('/job/complete/' + job, {
                        **report,
                        **error
                    })

            finally:
                # Delete tmp working directory
                if os.path.exists('./tmp'):
                    shutil.rmtree('./tmp')

                # Post Logs to elastic 
                endtime = datetime.utcnow()    
                elastic_url = os.getenv('ELASTIC_URL')
                if not elastic_url:
                    log("ELASTIC_URL environment variable is not set.")
                    raise Exception("Missing ELASTIC_URL environment variable.")
                # read the all the logs from the log file
                with open('job.log', 'r') as f:
                    logs = f.readlines()

                data = {
                    "jobId": job,
                    "moduleId": module_id,
                    "teamId": team,
                    "stackId": stack,
                    "documentId": document,
                    "request": req,
                    "logs": logs,
                    "error": error,
                    "duration": (endtime - starttime).total_seconds(),
                    "completed": False if error else True,  
                    "timestamp": datetime.utcnow().isoformat() + "Z"  
                }
                
                res = sess.post(elastic_url, 
                                data=json.dumps(data), 
                                headers={"Content-Type": "application/json"})
                
                print("Elastic response:", res.status_code, res.text) 

                # Close the logger listener
                log_listener.stop()

                # Close and remove all handlers from the logger
                for handler in logger.handlers:
                    handler.close()
                    logger.removeHandler(handler)

                # Ensure the logger is properly shut down
                logging.shutdown()

                # Delete the log file as well
                if os.path.exists('./job.log'):
                    os.remove('./job.log')
                
        return inner
    return wrapper