# Abre todos os datasets PDA ainda pendentes no browser para download manual.
# Apos baixar cada arquivo, execute:
#   python scripts/register_snapshot.py <slug> <caminho_do_arquivo>
#
# Exemplo:
#   python scripts/register_snapshot.py ancine-salas-exibicao-complexos Downloads/salas-exibicao.csv

$pendentes = @(
    # slug | url
    "ancine-atividades-economicas-agentes|https://dados.gov.br/dados/conjuntos-dados/atividades-economicas-dos-agentes-regulares-registrados-na-ancine"
    "ancine-produtoras-independentes|https://dados.gov.br/dados/conjuntos-dados/produtoras-independentes-regulares-registradas-na-ancine"
    "ancine-canais-programadoras|https://dados.gov.br/dados/conjuntos-dados/canais-de-programacao-de-programadoras-ativos-credenciados-na-ancine"
    "ancine-canais-distribuicao-obrigatoria|https://dados.gov.br/dados/conjuntos-dados/canais-de-programacao-de-distribuicao-obrigatoria-ativos-credenciados-na-ancine"
    "ancine-salas-exibicao-complexos|https://dados.gov.br/dados/conjuntos-dados/salas-de-exibicao-e-complexos-registrados-na-ancine"
    "ancine-obras-fomento-indireto|https://dados.gov.br/dados/conjuntos-dados/obras-nao-publicitarias-brasileiras-com-fomento-indireto-aprovado-na-ancine-leis-de-incentivo-federa"
    "ancine-pais-origem-obras-br|https://dados.gov.br/dados/conjuntos-dados/pais-de-origem-das-obras-nao-publicitarias-brasileiras"
    "ancine-obras-estrangeiras-roe|https://dados.gov.br/dados/conjuntos-dados/obras-nao-publicitarias-estrangeiras-relacao-de-todos-os-roes-emitidos-excluindo-se-a-categoria-de-r"
    "ancine-diretores-obras-estrangeiras|https://dados.gov.br/dados/conjuntos-dados/diretores-de-obras-nao-publicitarias-estrangeiras-roe"
    "ancine-produtores-obras-estrangeiras|https://dados.gov.br/dados/conjuntos-dados/produtores-de-obras-nao-publicitarias-estrangeiras-roe"
    "ancine-pais-origem-obras-estrangeiras|https://dados.gov.br/dados/conjuntos-dados/pais-de-origem-de-obras-nao-publicitarias-estrangeiras-roe"
    "ancine-bilheteria-diaria-distribuidoras|https://dados.gov.br/dados/conjuntos-dados/relatorio-de-bilheteria-diaria-de-obras-informadas-pelas-distribuidoras"
    "ancine-grupos-economicos|https://dados.gov.br/dados/conjuntos-dados/relacao-de-grupos-economicos"
    "ancine-crt-obras-nao-publicitarias|https://dados.gov.br/dados/conjuntos-dados/crt-obras-nao-publicitarias-registradas"
    "ancine-crt-obras-publicitarias|https://dados.gov.br/dados/conjuntos-dados/crt-obras-publicitarias-registradas"
    "ancine-bilheteria-diaria-exibidoras|https://dados.gov.br/dados/conjuntos-dados/relatorio-de-bilheteria-diaria-de-obras-informadas-pelas-exibidoras"
    "ancine-fsa-investimento-contratados|https://dados.gov.br/dados/conjuntos-dados/projetos--de-investimento-contratados-no-ambito-do-fsa"
    "ancine-prestacao-contas-processos|https://dados.gov.br/dados/conjuntos-dados/relacao-de-processos-em-fase-de-prestacao-de-contas"
    "ancine-filmagem-estrangeira|https://dados.gov.br/dados/conjuntos-dados/filmagem-estrangeira-relacao-de-producao-de-obras-audiovisuais-estrangeiras-em-territorio-nacional"
    "ancine-salas-exibicao-evolucao|https://dados.gov.br/dados/conjuntos-dados/salas-de-exibicao---evolucao-anual"
    "ancine-lancamentos-distribuidoras|https://dados.gov.br/dados/conjuntos-dados/lancamentos-comerciais-por-distribuidoras"
    "ancine-agentes-economicos-estrangeiros|https://dados.gov.br/dados/conjuntos-dados/agentes-economicos-estrangeiros"
    "ancine-complexos-cinematograficos-evolucao|https://dados.gov.br/dados/conjuntos-dados/complexos-cinematograficos---evolucao-anual"
)

Write-Host ""
Write-Host "=== 23 datasets PDA pendentes ==="
Write-Host ""
$i = 0
foreach ($entry in $pendentes) {
    $parts = $entry -split "\|"
    $slug = $parts[0]
    $url  = $parts[1]
    $i++
    Write-Host "[$i/23] $slug"
    Write-Host "      $url"
    Write-Host ""
}

$abrir = Read-Host "Abrir TODOS os 23 no browser? (s/n)"
if ($abrir -eq "s" -or $abrir -eq "S") {
    foreach ($entry in $pendentes) {
        $url = ($entry -split "\|")[1]
        Start-Process $url
        Start-Sleep -Milliseconds 800
    }
    Write-Host ""
    Write-Host "23 abas abertas. Baixe cada CSV e registre com:"
    Write-Host "  python scripts/register_snapshot.py <slug> <arquivo>"
}
