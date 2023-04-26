from flask import Flask, request, jsonify, send_file, render_template
from pandas import read_excel, ExcelWriter
from os import getcwd
from json import loads
from env import ADMIN, SECRET, PORT
app = Flask(__name__,template_folder="templates") # Criando aplicação
@app.route("/clients", methods=["GET","POST"]) # Rota /clients
def clients(): # Função de controlador das rotas do cliente
    filename = f'{getcwd()}/app/data/clients.xlsx' # Caminho para o arquivo exel
    if request.method == "GET": # Caso o metodo seja get
        args = request.args # Query
        try:
            exelData = read_excel(filename) # tentando carregar exel
        except:
            return jsonify({"error":"Erro ao tentar acessar a planilha de dados."}) # retornando erro
        if args.get("geral_numeroregistro"): # Se tiver uma query com numero de registro 
            register = args.get("geral_numeroregistro") # Pegando numero de registro
            client = exelData.loc[exelData["geral_numeroregistro"] == register.strip()] # Localizando por numero de registro
            if not client.empty: # Verificando se existe o cliente
                exelData = exelData.loc[exelData["hosp_numeroreserva"] == client.iloc[0]["hosp_numeroreserva"]] # Localizando pelo numero de reserva
            else: # Caso não exista
                exelData = client # Passando uma array vazia
        elif args.get("hosp_qtdevagas"): # Se tiver uma query com id
            id = args.get("hosp_qtdevagas") # Pegando o id
            exelData = exelData.loc[exelData["hosp_qtdevagas"] == int(id)] # Passando o cliente
        elif args.get("hosp_numeroreserva"): # Caso haja um get com o numero de reserva
            reserv = args.get("hosp_numeroreserva") # Pegando o numero de reserva
            exelData = exelData.loc[exelData["geral_numeroregistro"] == reserv] # Localizando um cliente pelo numero de reserva
        jsonData = exelData.to_json(orient='records') # Passando para json
        jsonData = loads(jsonData) # Carregando objeto em json
        return jsonify({"data": jsonData}), 200
    if request.method == "POST":
        args = request.args # Pegando o query
        if args.get("username") != ADMIN or args.get("password") != SECRET: # Conferindo login com o env
            return "Falha ao realizar o login." # Mensagem de erro
        files = request.files # Pegando os arquivos da request
        print(files)
        if not files.get("clients"): # Vendo se existe algum arquivo
            return "Não foi encontrado nenhum arquivo"
        file = files['clients'] # Pegando especificadamente o arquivo clients
        # Verifica se o arquivo tem uma extensão permitida
        if file and file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            # Salva o arquivo em disco
            file.save(filename)
            return "Arquivo salvo com sucesso!" # Enviando mensagem de sucesso
        return "Falha ao salvar o arquivo." # Enviando erro
@app.route("/download", methods=["GET"])
def dowload(): # Função para fazer o dowload do arquivo exel
    args = request.args # Pegando o query
    if args.get("username") != ADMIN or args.get("password") != SECRET: # Verificando o login com o env
        return jsonify({"error":"Credenciáis inválidas."}) # Retornando erro
    # Carregando o arquivo Excel do disco
    filename = f'{getcwd()}/app/data/clients.xlsx' # Nome do arquivo exel
    exelData = read_excel(filename) # Lendo o arquivo exel usando o pandas
    if exelData.empty:
        return jsonify({"msg":"Não possui nenhuma planilha dentro do servidor."})
    # Escrevendo o DataFrame em um arquivo Excel temporário
    with ExcelWriter(filename) as writer:
        exelData.to_excel(writer, index=False)
    # Enviando o arquivo Excel para o cliente
    return send_file(filename, as_attachment=True)
@app.route("/login", methods=["POST"])
def login(): # Rota para conferir o login
    if request.method == "POST": # Metodo POST
        args = request.args # Pegando o query
        if args.get("username") != ADMIN or args.get("password") != SECRET: # Verificando o login com o env
            return jsonify({"error":"Credenciáis inválidas."}) # Retornando erro
        return jsonify({"msg":"Usuário logado com sucesso."}) # Retornando sucesso
@app.route("/admin",methods=["GET"])
def adminTemplate(): # Rota do painel do administrador 
    return render_template("admin.html") # Renderizando o template
@app.route("/",methods=["GET"])
def consultTemplate(): # Rota do painel de consulta
    return render_template("index.html") # Renderizando o template
if __name__ == "__main__": 
    app.run('0.0.0.0',port=PORT,debug=True) # Rodando o servidor debug