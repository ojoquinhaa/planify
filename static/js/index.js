// O código abaixo é executado quando o documento HTML correspondente é carregado no navegador
$(document).ready(function () {
  // Cria variáveis para cada elemento HTML do formulário que será manipulado mais tarde.
  const consult = $("#consult");
  const send = $("#send");
  const hosp = $("#hosp");
  const reserv = $("#reserv");
  const id = $("#id");
  const category = $("#category");
  const pous = $("#pous");
  const indate = $("#in");
  const outdate = $("#out");
  const query = $("#query");

  // Esta função preenche os campos de reserva, ID, categoria e pousada com os valores correspondentes
  function organizate(r, i, c, p) {
    reserv.val(r);
    id.val(i);
    category.val(c);
    pous.val(p);
  }

  // Esta função popula a lista de opções do elemento 'hosp' com os valores correspondentes à consulta de dados do servidor
  async function getSelect(data) {
    const number = consult.val().toUpperCase().trim();
    $("#query tr").remove();
    const table = [];
    data.forEach((c) => {
      if (String(c.geral_numeroregistro).trim().toUpperCase() === number) {
        const option = $("<option></option>");
        option.text(`${c.hosp_nomehospede} (${c.hosp_numeroreserva})`);
        option.val(c.hosp_qtdevagas);
        hosp.append(option);
      }
    });
  }

  // Esta função cria uma tabela HTML com os resultados da consulta ao servidor e a insere no elemento 'query'
  async function getTable(client) {
    $("#query tr").remove();
    const search = await fetch(
      "/clients?hosp_numeroreserva=" + client.hosp_numeroreserva
    ).then((j) => j.json());
    const data = search.data;
    data.forEach((c) => {
      if (c.hosp_nomehospede == null) {
        return;
      }
      const type = $("<th></th>");
      const register = $("<th></th>");
      const name = $("<th></th>");

      type.text(c.hosp_tipoquarto);
      register.text(c.geral_numeroregistro);
      name.text(c.hosp_nomehospede);

      const tr = $("<tr></tr>");
      tr.append(type);
      tr.append(register);
      tr.append(name);

      query.append(tr);
    });
  }

  // Esta função é acionada quando o valor do elemento 'hosp' é alterado, busca os dados do cliente correspondente no servidor e chama outras funções para preencher a tabela e os campos do formulário.
  hosp.on("change", async () => {
    const id = hosp.val();
    const dataframe = await fetch(`/clients?hosp_qtdevagas=${id}`).then((j) =>
      j.json()
    );
    if (dataframe.length === 0) {
      return;
    }
    const client = dataframe.data[0];
    organizate(
      client.hosp_numeroreserva,
      client.geral_idsistema,
      client.hosp_categoriapacote,
      client.hosp_nomepousada
    );
    getTable(client);
  });

  // Esta função é acionada quando o botão 'send' é clicado, busca os dados do cliente correspondente no servidor e chama outras funções para preencher a tabela e os campos do formulário.
  send.on("click", async () => {
    const number = consult.val();
    const dataframe = await fetch(
      `/clients?geral_numeroregistro=${number}`
    ).then((j) => j.json());

    const data = dataframe.data;

    if (data.length === 0 || data.length > 100) {
      return;
    }

    $("#hosp option").remove();

    const client = data[0];

    organizate(
      client.hosp_numeroreserva,
      client.geral_idsistema,
      client.hosp_categoriapacote,
      client.hosp_nomepousada
    );

    getSelect(data);

    getTable(client);
  });
});
