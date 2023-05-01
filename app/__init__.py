from flask import Flask, request, jsonify, send_file, render_template
from pandas import read_excel, ExcelWriter, DataFrame, concat, io
from os import getcwd
from json import loads
from env import ADMIN, SECRET, PORT
from numpy import array
app = Flask(__name__,template_folder="templates",static_folder='../static') # Criando aplicação
@app.route("/clients", methods=["GET","POST", "PUT", "DELETE"]) # Rota /clients
def clients(): # Função de controlador das rotas do cliente
    filename = f'{getcwd()}/app/data/clients.xlsx' # Caminho para o arquivo exel
    args = request.args # Pegando o query
    body = request.form # Pegando o formulario
    if request.method != "GET":
        if args.get("username") != ADMIN or args.get("password") != SECRET: # Verificando o login com o env
            return jsonify({"error":"Credenciáis inválidas."}), 403 # Retornando erro
    try:
        exelData = read_excel(filename) # tentando carregar exel
    except:
        return jsonify({"error":"Erro ao tentar acessar a planilha de dados."}), 500 # retornando erro
    if request.method == "GET": # Caso o metodo seja get
        if args.get("geral_numeroregistro"): # Se tiver uma query com numero de registro 
            register = args.get("geral_numeroregistro") # Pegando numero de registro
            exelData = exelData.loc[exelData["geral_numeroregistro"].str.upper().str.strip() == register.strip().upper()] # Localizando por numero de registro
        elif args.get("hosp_qtdevagas"): # Se tiver uma query com id
            id = args.get("hosp_qtdevagas") # Pegando o id
            exelData = exelData.loc[exelData["hosp_qtdevagas"] == int(id)] # Passando o cliente
        elif args.get("hosp_numeroreserva"): # Caso haja um get com o numero de reserva
            reserv = args.get("hosp_numeroreserva") # Pegando o numero de reserva
            exelData = exelData.loc[exelData["hosp_numeroreserva"] == int(reserv)] # Localizando um cliente pelo numero de reserva
        jsonData = exelData.to_json(orient='records') # Passando para json
        jsonData = loads(jsonData) # Carregando objeto em json
        return jsonify({"data": jsonData}), 200
    if request.method == "POST": # Caso o metodo for post
        df = DataFrame(body, columns=exelData.columns, index=[0]) # Criando um dataframe com o body passado
        exelData = concat([exelData,df],ignore_index=True) # Contatenando os dois novos exel
        exelData.drop([col for col in exelData.columns if 'Unnamed:' in col], axis=1, inplace=True)
        exelData.to_excel(filename) # Salvando o novo arquivo
        return jsonify({"msg":"Cliente adicionado com sucesso!"}) # Enviando mensagem de sucesso
    if request.method == "DELETE": # Caso o metodo seja delete
        id = args.get("hosp_qtdevagas") # Pegando o id
        client = exelData.loc[exelData["hosp_qtdevagas"] == int(id)] # pegando o cliente do id inserido
        if client.empty: # Se o cliente for vazio
            return jsonify({"error":"O cliente não foi encontrado."}), 400 # Retorna erro
        exelData = exelData.drop(client.index) # Removendo o cliente 
        exelData.drop([col for col in exelData.columns if 'Unnamed:' in col], axis=1, inplace=True)
        exelData.to_excel(filename) # Salvando arquivo
        return jsonify({"msg":"Arquivo deletado com sucesso."}), 200 # Retorna mensagem de sucesso
    if request.method == "PUT":
        id = args.get("hosp_qtdevagas") # Pegando o id
        exelData.drop([col for col in exelData.columns if 'Unnamed:' in col], axis=1, inplace=True)
        row_idx = exelData.index[exelData['hosp_qtdevagas'] == int(id)][0]
        for col, val in body.items():
            exelData.at[row_idx, col] = val
        exelData.to_excel(filename) # Salvando arquivo
        return jsonify({"msg":"Arquivo modificado com sucesso!"}), 200 # Retorna mensagem de sucesso
@app.route("/download", methods=["GET", "POST"])
def dowload(): # Função para fazer o dowload do arquivo exel
    filename = f'{getcwd()}/app/data/clients.xlsx' # Caminho para o arquivo exel
    if request.method == "GET":
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
    if request.method == "POST":
        args = request.args # Pegando o query
        if args.get("username") != ADMIN or args.get("password") != SECRET: # Conferindo login com o env
            return "Falha ao realizar o login." # Mensagem de erro
        files = request.files # Pegando os arquivos da request
        if not files.get("clients"): # Vendo se existe algum arquivo
            return "Não foi encontrado nenhum arquivo"
        file = files['clients'] # Pegando especificadamente o arquivo clients
        # Verifica se o arquivo tem uma extensão permitida
        if file and file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            # Salva o arquivo em disco
            file.save(filename)
            return "Arquivo salvo com sucesso!" # Enviando mensagem de sucesso
        return "Falha ao salvar o arquivo." # Enviando erro
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