<h1>Automação para registros de Danfes</h1>
<p>
  Uma simples automação utilizando Python, feita para ler um arquivo '.pdf' onde posso ter uma ou mais Danfes.
  
  Utilizo bibliotecas como Openpyxl, Pdfplumber e Pandas, identifico o começo de uma nova Danfe, pelo numero de folha da nota, onde cada 'fl 1.' representa a primeira pagina de uma Danfe, onde nessa primeira pagina possuo todas as informações que preciso, sendo assim meu programa não precisa fazer um ciclo completo analisando outras paginas que não possuem nenhuma informação que preciso.

  Utilizo Regex, para ler o arquivo bruto que me é gerado após o programa ler a pagina com as informações necessarias e logo em seguida e insere minhas informações na minha planilha de Excel, onde tenho tratamentos feitos dentro da planilha Excel também!
</p>
