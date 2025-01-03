import mysql.connector

def create_connection():
    
    connection = mysql.connector.connect(
        host="localhost", ## böyle kalsın
        user="root",      ## user değiştirmediysen böyle geliyor
        password="1234",  ## şifreni değiştir
        database="proje"  ## schemanın adını proje olarak yapmadıysan değiştir burayı
    )
    return connection