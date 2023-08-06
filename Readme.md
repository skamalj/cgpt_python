# QnA with OpenAI
Code for this is in `qna` folder.

Implementation of the same is detailed in this [blog](https://www.kamalsblog.com/2023/07/Leveraging-Text-Embeddings-for-QnA.html)

## Env
Set OPENAI_API_KEY environment variable to your OPENAI Key. This is required by all demos in this repo.

## Create Embedding

* Book is [here](https://ncert.nic.in/textbook/textbook.php?kesp1=0-8). Download chapters of this book and copy it to S3 location.
* Modify the code `create_embedding.py` for your bucket path and folder. output folder does not matter, embeddings are stored in local directory.
* These embeddings are then loaded by `detect.py`. If you change the filenames in anyway, then update this code.
* To create embedding run the following command. File must be .pdf. This is sent to textract for text extraction and then embedding is created for each page. This is then stored in _embedding.csv file in local directory as well as .txt file with all the text returned by textract in one file. 
* * These extra txt files are not used in this demo, but are used in 'Summarization' demo. so if you want you can delete these from here or move to summarization folder.
```
python create_embedding.py <filename.pdf>
```

## Runnning the demo
* Execute the API backend
```
python detect.py
```
* Open frontend in browser i.e index.html (open directly, this is not served via backend) and then ask some questions from the story. You can choose some from below or you can create your own after reading the stories. Better you get your own pdf document and use it for this demo.

## Why Embedding
First ask any question from below and check the `full` checkbox. This will submit the whole chapter to the openai, you will see that this will definitely fail for chapter 3 and may be for others as well due to token limits.

## Sample questions

### Chapter 1 and 2
* where did mrs dorling lived 
* Why did the narrator of the story want to forget the address
* what happened to table silver
* why mrs dorling took belongings of narrators mother
* why did boys return the horse
* who was mourad

### Mother(ch 3)
* How does Mrs. Pearson feel about her family's treatment of her, and why is she hesitant to stand up for herself?
* What is Mrs. Fitzgerald's role in the play, and how does she influence Mrs. Pearson?
* How does Mrs. Pearson's behavior change after the body switch with Mrs. Fitzgerald, and how do her family members react to her new demeanor?
* How do Doris and Cyril Pearson initially respond to their mother's changed behavior, and what is their opinion of her actions?
* What impact does Mrs. Pearson's newfound assertiveness have on her husband, George, and his perception of himself within the family and the community?

### Ghat (Ch4)
* Who is the dying man in the story, and what is his request to Amitav?
* How did Shahid's illness affect his friendship with Amitav?
* What kind of poet was Shahid, and how did his poetry differ from contemporary styles?
* What was Shahid's passion besides poetry and writing?
* When and how did Shahid pass away, and what impact did it have on Amitav?

### Birth (Ch5)
* What is the significance of Joe Morgan's visit to Andrew?
* What challenges does Andrew face during the delivery and resuscitation of the child, and how does he handle the situation?
* what happened to susan during delivery?
* What does the successful revival of the baby mean to Andrew?
* How does Joe Morgan react to the outcome of the childbirth?

### Melon City (ch6)
* How did the architect defend himself when he was accused by the King?
* IWhat unfortunate incident occurred when the King rode under the arch?
* Why were the workmen and masons also blamed by the King?
* How did the King eventually meet his fate?


## Summarization
* Similarly for summarization, execute the corresponding summary.py (only one of the two APIs  runs as they are on same port, change the port if you want to run them together)

## Health Bot
Main code is in main.py and function definition is in functions.json