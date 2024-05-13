### Project structure
```
.
├── docker-compose.yaml
├── fake_data_scripts.py
├── server
    ├── Dockerfile
    ├── requirements.txt (Missing) 
    ├── server.py
    └── db_sql
	├── db_sqlite3.py
	└── SensorValues.db

```

### How to run
First create an environment:  
`python -m venv myenv`
  
Second source the environment:  
`source myenv/bin/activate`  

Third install the libraries with requirements.txt:  
`pip install -r requirements.txt`  
  
Run the server.py using flask:  
`python3 -m flask --app main run`  
  
This should start a "webserver" that can be accessed using the ip address shown in the terminal.
