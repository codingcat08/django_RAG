# django_RAG

                     

 DJANGO_PROJECT/
   
    ├── backend/			          - basic Django app configurations 
    
        │   ├── __init__.py
        
        │   ├── asgi.py
        
        │   ├── settings.py
        
        │   ├── urls.py
        
        │   └── wsgi.py

    ├── documents/                                              -backend for processing the pdf and question 
    
        │   ├── migrations/
        
        │   ├── __init__.py
        
        │   ├── admin.py
        
        │   ├── apps.py
        
        │   ├── models.py
        
        │   ├── serializers.py
        
        │   ├── tests.py
        
        │   ├── text_processing.py
        
        │   ├── urls.py
        
        │   └── views.py

    ├── frontend/				- frontend folder 
    
    ├── media/                                                        - contains the uploaded documents 
    
    ├── .env                                                             - contains secret api keys (insert your open ai api key here)
    
    ├── docker-compose.yml                                - orchestrates db and web containers together
    
    ├── Dockerfile                                                   - defines the web container image 
    
    ├── entrypoint.sh                                             -bash file to automate migrations
    
    ├── init-db.sql                                                    -example structure of table 
    
    ├── manage.py                                                 -helps to interact the Django project 
    
    ├── README.md                                              -contains info on how to use repo 
    
    └── requirements.txt                                         -contains all required python libraries

![image](https://github.com/user-attachments/assets/ed09b389-2bc2-4363-acf9-3bcc4b98fb39)


Steps ->

1.  git clone https://github.com/codingcat08/django_RAG.git
2. Open any terminal and go the the repo location 
3. put open ai api key in .env 
4. cd frontend
5. npm install 
6. npm start (for starting frontend)
7. cd.. (back to root of the directory)
8. docker-compose up --build  (start the backend and database containers)  

(if the entrypoint.sh file doesn’t run in step 8 you can try changing the default spacing from crlf to lf in windows )
 
The app will start running at http://localhost:3000/

 
 ![image](https://github.com/user-attachments/assets/508a11b4-46ea-4f43-bab5-032746b6e365)


      
Additional functionalities ->
1. you can add multiple pdfs and ask question from any uploaded pdf 
2. if you refresh the page database gets cleared and you have a new session  
3. Frontend is not containerized in docker whereas backend and docker are .




     
       

