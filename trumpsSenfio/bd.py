import mysql.connector
import datetime
import time

def dbConnect():
  mydb = mysql.connector.connect(
  host="0.0.0.0",
  user="root",
  passwd="Jom@1234",
  database="SenfioDB" )
  return mydb


def insertFuncionario(id, nome, mydb):
  mycursor = mydb.cursor()
  sql = "INSERT INTO funcionario (id, nome) VALUES (%s, %s)"
  val = id, nome
  mycursor.execute(sql, val)
  mydb.commit()

def insertLocal(id, local, mydb):
  mycursor = mydb.cursor()
  sql = "INSERT INTO locais (id, nomeLocal) VALUES (%s, %s)"
  val = id, local
  mycursor.execute(sql, val)
  mydb.commit()

def insertEvento(idFunc,evento, idLocal, mydb):
  mycursor = mydb.cursor()

  now = datetime.datetime.now()
  ultimo = getLastEvent(idFunc, mydb)
  dif_seconds = (now - ultimo[1]).seconds
  
  if dif_seconds > 120 or evento != ultimo[0]:
    print('salvou!')
    date = now.strftime('%Y-%m-%d %H:%M:%S')
    val = idFunc, evento, idLocal, date
    sql = "INSERT INTO eventos (idFuncionario, evento, idLocal, dataHora) VALUES (%s, %s, %s, %s)"
    mycursor.execute(sql, val)
    mydb.commit()

def getLastEvent(idFunc, mydb):
  mycursor = mydb.cursor()
  sql = "SELECT eventos.evento, eventos.dataHora FROM eventos INNER JOIN funcionario ON eventos.idFuncionario = funcionario.id INNER JOIN locais on eventos.idLocal = locais.id  WHERE idFuncionario = %s"
  val = [idFunc]
  mycursor.execute(sql, val)
  myresult = mycursor.fetchall()
  if myresult:
    return myresult[-1]
  else:
    return ('saiu', datetime.datetime(1970, 1, 1, 0, 0, 0)) # Returns Epoch time

def buscarEventoFuncionario(idFunc, mydb):
  mycursor = mydb.cursor()
  sql = "SELECT funcionario.nome, locais.nomeLocal, eventos.evento, eventos.dataHora FROM eventos INNER JOIN funcionario ON eventos.idFuncionario = funcionario.id INNER JOIN locais on eventos.idLocal = locais.id  WHERE idFuncionario = %s"
  val = [idFunc]
  mycursor.execute(sql, val)
  myresult = mycursor.fetchall()
  for x in myresult:
    nomeFunc = x[0]
    nomeLocal = x[1]
    evento = x[2]
    date = x[3].strftime('%Y-%m-%d %H:%M:%S')
    print(nomeFunc+ ', ' +nomeLocal+', '+evento+', '+date)
    
def countPeople(nomelocal, mydb):
  mycursor = mydb.cursor()
  sql = "SELECT COUNT(*) FROM eventos INNER JOIN locais on eventos.idLocal = locais.id WHERE locais.nomeLocal = %s AND eventos.evento = 'entrou'"
  val = [nomelocal]
  mycursor.execute(sql, val)
  myresult = mycursor.fetchone()
  print("No total "+str(myresult[0])+" pessoas entraram neste local")



#Conectar no Banco de Dados
#insertFuncionario("pedro", mydb) #inserir funcionario
#insertLocal("sala1", mydb) #inserir novo local
#insertEvento(1, "entrou", 1, mydb) #inserir novo evento
#buscarEventoFuncionario(1, mydb)
