import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Lalitha@2006",
    database="placement_portal"
)

cursor = connection.cursor()