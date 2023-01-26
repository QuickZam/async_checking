import banana_dev as banana
import asyncio
import os, re, requests  
from pytube import extract 
from youtube_transcript_api import YouTubeTranscriptApi
from flask import Flask, request 
from logger import logger 
from doctr.io import DocumentFile  
from doctr.models import ocr_predictor

app = Flask(__name__) 
model = ocr_predictor(pretrained=True)

@app.route('/')
def home(): 
    return "Your app is working!"

async def question_image(link, file_type, content_type): 
    logger.info(f"Function name => question_image: Got the input\nFilePath: {link}")
    if link.endswith('.pdf'): 
        logger.info(f"File is PDF")
        doc = DocumentFile.from_pdf(link)
    else:
        logger.info("file is image")
        doc = DocumentFile.from_images(link)
    
    result = model(doc)
    text = result.render()
    text = text.replace('\n', '')
    logger.info(f"Text Extracted by OCR: {text}")
    task = asyncio.create_task(long_running_task_text(text, file_type, None))
    
async def request_api(summa): 
  logger.info("Function name => request_api: Got the input\nInput: {summa}")
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',}
  data = f"text={summa}"
  response = requests.post('http://bark.phon.ioc.ee/punctuator', headers=headers, data=data)
  logger.info("Function name => request_api: Got the output\nOutput: {response.text}")
  
  return response.text

async def banana_mcq(text, api_key, model_key): 
    payload = {"text": text, 'condition': False}
    logger.info("Function name => banana_mcq: Got the input")
    logger.info(f"Payload: {payload}")
    
    out = banana.run(api_key, model_key, payload)
    out = out['modelOutputs'][0]['output'][0]
    
    logger.info(f"Function name => banana_fn: Got the output: {out}")
    
    payload = {'output': out}
    response = requests.request("PATCH", url, headers=headers, data=payload)
    logger.info(f"Response result: {response}")
    # INSERT UPDATE CODE HERE! 
    
    
    
async def banana_fn(text, api_key, model_key): 
    payload = {"text": text}
    logger.info("Function name => banana_fn: Got the input")
    logger.info(f"Payload: {payload}")
    
    out = banana.run(api_key, model_key, payload)
    out = out['modelOutputs'][0]['html']
    
    logger.info(f"Function name => banana_fn: Got the output: {out}")

    payload = {'output': out}
    response = requests.request("PATCH", url, headers=headers, data=payload)
    logger.info(f"Response result: {response}")
    # INSERT UPDATE CODE HERE! 

    
    
    
async def text_(text, question_type): 
    api_key = "ec49909f-3d2f-4044-8882-535e3ce8a383"
    model_key = "7734639e-bcae-41f6-b7b9-47a9cbba26e1"
    
    payload = {'link': text}
    logger.info(f"Function Name => text_ Payload: {payload}")
    out = banana.run(api_key, model_key, payload)
    out = out['modelOutputs'][0]['text']
    logger.info(f"Function Name => text_ Got the output: {out}")
    
    if question_type == 'Fill in the Blanks': 
        api_key = "ec49909f-3d2f-4044-8882-535e3ce8a383"
        model_key = "389eaf12-4801-4673-bd57-52140c4cc90c"
        logger.info("Function Name => text_ : Got the output text, Now sent text to banana for making question!")
        logger.info(f"Function Name => text_ : Question_type: {question_type}")
        payload = {"text": out}
        logger.info(f"Function Name => text_ : Payload: {payload}")
        out = banana.run(api_key, model_key, payload)
        out = out['modelOutputs'][0]['html']
        logger.info(f"Function Name => text_ Got the output: {out}")
        payload = {'output': out}
        response = requests.request("PATCH", url, headers=headers, data=payload)
        logger.info(f"Response result: {response}")

        logger.info(f"Response result: {response.text}")
    
    elif question_type == 'Multiple Choice Questions (MCQ)':
        api_key = "ec49909f-3d2f-4044-8882-535e3ce8a383"
        model_key = "ddd49032-854c-4bb3-a368-9fd5b8c85646" 
        payload = {'text': out, 'condition': False}
        logger.info(f"Function Name => text_ : Question_type: {question_type}")
        logger.info(f"Function Name => text_ : Payload: {payload}")
        out = banana.run(api_key, model_key, payload)
        out = out['modelOutputs'][0]['output'][0]
        logger.info(f"Function Name => text_ Got the output: {out}")
        payload = {'output': out}
        response = requests.request("PATCH", url, headers=headers, data=payload)
        logger.info(f"Response result: {response}")

async def long_running_task_text(text, file_type, question_type):
    if file_type == 'Fill in the Blanks': 
        api_key = "ec49909f-3d2f-4044-8882-535e3ce8a383"
        model_key = "389eaf12-4801-4673-bd57-52140c4cc90c"
        
        out = await asyncio.create_task(banana_fn(text, api_key, model_key))
        loop.stop()
    
    elif file_type == 'Multiple Choice Questions (MCQ)':
        api_key = "ec49909f-3d2f-4044-8882-535e3ce8a383"
        model_key = "ddd49032-854c-4bb3-a368-9fd5b8c85646" 
        
        out = await asyncio.create_task(banana_mcq(text, api_key, model_key))
        loop.stop()
        
    elif file_type == "TEXT": 
        out = await asyncio.create_task(text_(text, question_type))
        loop.stop()
        
async def long_running_task_video(link, file_type): 
    try: 
        video_id = extract.video_id(link)
        logger.info(f"Function Name => long_running_task_video : {video_id}")
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = ' '.join([ i['text'].replace('\n', '') for i in transcript])
        text = re.sub('[^a-zA-Z0-9]', ' ', text)
        text = await asyncio.create_task(request_api(text)) 
        logger.info(f"Function Name => long_running_task_video : Transcript found: {text}")
        logger.info(f"Function Name => long_running_task_video : So sent to banana for making Question!")
        task = asyncio.create_task(long_running_task_text(text, file_type, None))
    
    except Exception as e:
        logger.error(f"Exception: {str(e)}") 
        logger.info(f"Function Name => long_running_task_video : Transcript not found: {link}")
        logger.info(f"Function Name => long_running_task_video : So sent to Banana")
        
        out = asyncio.create_task(long_running_task_text(link, 'TEXT', file_type))
    
async def api_handler(text, file_type, content_type):
    if content_type == 'TEXT': 
        task = asyncio.create_task(long_running_task_text(text, file_type, None))
    
    elif content_type == 'VIDEO':
        task = asyncio.create_task(long_running_task_video(text, file_type))
        
    elif content_type == 'DOCUMENT': 
        task = asyncio.create_task(question_image(text, file_type, content_type))

    return {"status": "processing"}


@app.route('/text_to_question', methods = ['POST', 'GET'])    
async def executer(): 
    global url, headers
    unique_id = request.args.get('unique_id')
    url = f"https://chitramai.com/version-test/api/1.1/obj/Question_generation/{unique_id}"
    headers = {'Authorization': "Bearer e1a9185d16055bac44068c8ac1f0893a"}

    URL = f"https://chitramai.com/version-test/api/1.1/obj/Question_generation/{unique_id}"
    response = requests.request("GET", URL) 
    logger.info("APP_NAME: QuestGen \nGot the Input.\nFetching response: {response}")

    response = response.json()['response']
    file_type, filename = response['file_type'], response['filename']  
    question_type, text = response['question_type'], response['text']  

    logger.info(f"FileType: {file_type},\nFilename: {filename},\nQuetionType: {question_type},\nText: {text}")

    response = asyncio.create_task(api_handler(text, file_type, question_type))


    return response 


if __name__ == '__main__': 
    global loop 
    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(app.run())
    loop.run_forever()