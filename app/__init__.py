from flask import Flask, request, jsonify, send_file
from pandas import read_excel, ExcelWriter
from os import getcwd
from json import loads
from waitress import serve
app = Flask(__name__) # Criando aplicação
@app.route("/clients", methods=["GET","PUT"]) # Rota /clients
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
            client = exelData.loc[exelData["geral_numeroregistro"] == register] # Localizando por numero de registro
            if not client.empty: # Verificando se existe o cliente
                exelData = exelData.loc[exelData["hosp_numeroreserva"] == client.iloc[0]["hosp_numeroreserva"]] # Localizando pelo numero de reserva
            else: # Caso não exista
                exelData = client # Passando uma array vazia
        jsonData = exelData.to_json(orient='records') # Passando para json
        jsonData = loads(jsonData) # Carregando objeto em json
        return jsonify({"data": jsonData}), 200
    if request.method == "PUT":
        files = request.files # Pegando os arquivos da request
        file = files['clients'] # Pegando especificadamente o arquivo clients
        # Verifica se o arquivo tem uma extensão permitida
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            # Salva o arquivo em disco
            file.save(filename)
            return jsonify({"msg":"Arquivo salvo com sucesso!"}) # Enviando mensagem de sucesso
        return jsonify({"error":"Falha ao salvar o arquivo. O formato está inválido."}) # Enviando erro
@app.route("/download", methods=["GET"])
def dowload(): # Função para fazer o dowload do arquivo exel
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
if __name__ == "__main__":
    serve(app, '0.0.0.0', port=8080) # Rodando o servidor 