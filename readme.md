# Desenvolvendo uma API com a AWS Educate
## Dados sobre Ocorrências Criminais, SINESP - Ministério da Justiça obtidos pelo link:
### http://dados.gov.br/dataset/sistema-nacional-de-estatisticas-de-seguranca-publica

# Instalação

## 1 - Crie uma nova instância EC2 **Ubuntu** na AWS Educate, segue um tutorial de como criar uma instância na AWS: https://www.youtube.com/watch?v=4kufR3fFEjM
### 1.1 - Lembre-se de habilitar a porta 80 (HTTP) em sua instância para a API poder funcionar.

## 2 - Instale o Putty em seu computador para acessar sua instância EC2 utilizando o IP público do mesmo.
### 2.1 - Utilize o Putty para converter sua chave .pem para .ppk como mostrado no tutorial: https://medium.com/@praneeth.jm/launching-and-connecting-to-an-aws-ec2-instance-6678f660bbe6

## 3 - Execute a sequência de comandos abaixo no terminal da sua instância pelo Putty:
### 3.1 - Baixe o script de configuração do ambiente.
<code>wget https://raw.githubusercontent.com/SamuelHericles/Desenvolvendo_uma_API/master/02.C%C3%B3digos/configAPI.sh</code>

### 3.2 -  Conceda permissões de leitura e escrita ao script de configuração.
<code>sudo chmod 777 configAPI.sh</code>

### 3.3 - Execute-o.
<code>./configAPI.sh</code>

### 3.4 - Prontinho! A API já está no ar e aguardando por requisições. Olhe abaixo o que a mesma é capaz de retornar.

# Funcionamento

## Confira a documentação completa da API [aqui](https://docs.google.com/document/d/1yBTdEPZ05kxDgXAp0umdSry_XSp_ont2205MljGQAKA/edit?usp=sharing).

## Exemplos de requisições aceitas:

* Para requisitar toda a base de Ocorrências:
> <IP Público de sua instância>/ocorrencias?key=<API_KEY>
* Para obter os 10 maiores registros de vítimas:
> <IP Público de sua instância>/vitimas?key=<API_KEY>&ranking=10
* Para requistar as vítimas fatais do ano de 2018:
> <IP Público de sua instância>/vitimas?key=<API_KEY>&ano=2018
* Para obter as ocorrências de Estupro no mês de Janeiro em Tocantins:
> <IP Público de sua instância>/ocorrencias?key=<API_KEY>&uf=TO&crime=Estupro&mes=janeiro
* Para requisitar as vítimas fatais em Cruz-CE em Janeiro de 2020:
> <IP Público de sua instância>/vitimas_municipios?key=<API_KEY>&cid=Cruz&ano=2020&mes=jan&uf=ce
* Para requisitar a média de ocorrências a cada ano:
> <IP Público de sua instância>/info/media_ocorrencias_ano?key=<API_KEY>
* Para requisitar a soma das ocorrências em cada estado:
> <IP Público de sua instância>/info/soma_ocorrencias_estado?key=<API_KEY>
* Para requisitar a soma de ocorrências em cada tipo de crime:
> <IP Público de sua instância>/info/soma_ocorrencias_crime?key=<API_KEY>
* Para requisitar os 5 estados menos perigosos:
> <IP Público de sua instância>/info/menos_perigosos?key=<API_KEY>

## Em construção ...


## #Equipe4 - Ciência de Dados - Desenvolvendo uma Nova API

Feito com 💙 e Python