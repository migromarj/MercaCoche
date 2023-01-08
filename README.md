# <img src="https://github.com/migromarj/MercaCoche/blob/main/static/images/logo.png?raw=true" width="33"> MercaCoche

Website developed to help users find their ideal car, offering cars from the main second-hand car sales websites, such as [Autocasión](https://www.autocasion.com/coches-ocasion), [coches.com](https://www.coches.com/coches-segunda-mano/coches-ocasion.htm) and [motor.es](https://www.motor.es/coches-segunda-mano/).

## Local Installation

### Pre-requirements

- [Python 3.11.1](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

### Steps

1. To run the project locally, open a command console and run the following commands:

    ```
    pip install pipenv
    
    pipenv shell
    
    git clone https://github.com/migromarj/MercaCoche.git
  
    cd MercaCoche
  
    pip install -r requirements.txt
    ```
    
2. This project uses environment variables that need to be set before running the project, you will need to create a file called ".env" inside the directory with the following content:

    ```
    DJANGO_SECRET_KEY = 'django-insecure-+_1ct^%h8*2ht5z_zu#h)()hx%2$b*fip$rd6+jvxoh0y&m1l8'
    ```
    An example django secret key is given here, but the best option is to have it generated by the user himself, knowing that it is a key that is used to encrypt       sensitive data in the django application, and is at least 50 characters long.
    
3. Now we will proceed to run the project, executing the following commands in a console inside the directory:

    ```
    python manage.py makemigrations

    python manage.py migrate

    python manage.py runserver
    ```

4. If you've gotten to this point without any errors, you should be running the project locally successfully. You can access the initial route through the following link: [http://localhost:8000](http://localhost:8000)

## Web Images

<img width="1042" alt="MercaCoche load data" src="https://github.com/migromarj/Readme-Images/blob/master/MercaCoche/LoadData.png">
<img width="1042" alt="MercaCoche index" src="https://github.com/migromarj/Readme-Images/blob/master/MercaCoche/Index.png">
<img width="1042" alt="MercaCoche specific cars" src="https://github.com/migromarj/Readme-Images/blob/master/MercaCoche/SpecificCars.png">
<img width="1042" alt="MercaCoche car details first part" src="https://github.com/migromarj/Readme-Images/blob/master/MercaCoche/CarDetails1.png">
<img width="1042" alt="MercaCoche car details second part" src="https://github.com/migromarj/Readme-Images/blob/master/MercaCoche/CarDetails2.png">