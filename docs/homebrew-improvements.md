# Sugestões de Melhoria - Homebrew Distribution

Relatório gerado a partir do code review dos commits 72f1337 → 055447a.

## Correções Aplicadas ✅

### 1. Instalação editável no Homebrew Formula
- **Arquivo:** `Formula/metalscribe.rb`
- **Problema:** `pip install -e .` cria symlinks que quebram após cleanup do Homebrew
- **Correção:** Alterado para `pip install .`

### 2. Versão hardcoded no bloco test
- **Arquivo:** `Formula/metalscribe.rb`
- **Problema:** `/0\.1\.0/` falharia ao lançar nova versão
- **Correção:** Alterado para `/\d+\.\d+\.\d+/`

### 3. actions/setup-python desatualizado
- **Arquivo:** `.github/workflows/homebrew-test.yml`
- **Problema:** Usava v4 (deprecado), enquanto `ci.yml` usa v5
- **Correção:** Atualizado para v5

### 4. pytest não instalado no CI
- **Arquivo:** `.github/workflows/homebrew-test.yml`
- **Problema:** Job `test-suite` rodava pytest sem instalar
- **Correção:** Adicionado `pip install pytest`

---

## Melhorias Recomendadas 🔧

### Alta Prioridade

#### 1. SHA256 Placeholder
**Arquivo:** `Formula/metalscribe.rb` linha 5

O placeholder `HOMEBREW_SHA256_PLACEHOLDER` causará falha no `brew audit --strict`.

**Opções:**
- Calcular SHA256 real quando criar o release v0.1.0
- Ou condicionar o audit no CI para ignorar quando placeholder presente

```bash
# Calcular SHA256 do release
curl -sL https://github.com/feliperbroering/metalscribe/archive/refs/tags/v0.1.0.tar.gz | shasum -a 256
```

#### 2. post_install Longo (15-40 min)
**Arquivo:** `Formula/metalscribe.rb` linhas 40-77

Executar `doctor --setup` no `post_install` é incomum para Homebrew e pode:
- Causar timeouts em CI
- Bloquear usuários inesperadamente
- Falhar silenciosamente com problemas de rede

**Recomendação:** Tornar opt-in:

```ruby
def post_install
  system "#{bin}/metalscribe", "--version"
  
  puts "\n" + "="*75
  puts "✓ metalscribe installed successfully!"
  puts "="*75
  puts "\nTo complete setup (download models, compile whisper.cpp):"
  puts "  metalscribe doctor --setup"
  puts "\nThis takes 15-40 minutes on first run."
  puts "="*75 + "\n"
end
```

Ou adicionar fallback para não quebrar instalação:

```ruby
system "#{bin}/metalscribe", "doctor", "--setup" rescue nil
```

#### 3. Verificação de Curl Frágil
**Arquivo:** `scripts/homebrew/release.sh` linhas 29-33

**Problema:** Pipe para grep pode falhar silenciosamente.

**Correção sugerida:**
```bash
HTTP_STATUS=$(curl -sL -o /dev/null -w "%{http_code}" "$TARBALL_URL")
if [ "$HTTP_STATUS" != "200" ]; then
    echo "❌ Release $VERSION not found (HTTP $HTTP_STATUS)"
    exit 1
fi
```

---

### Média Prioridade

#### 4. Validação de Formato de Versão
**Arquivo:** `scripts/homebrew/release.sh`

Adicionar validação para evitar erros de digitação:

```bash
if [[ ! "$1" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Version must be in format vX.Y.Z (e.g., v0.1.0)"
    exit 1
fi
```

#### 5. Cache de Dependências no CI
**Arquivo:** `.github/workflows/homebrew-test.yml`

O workflow instala `python@3.11` e `ffmpeg` em cada execução. Considerar:

```yaml
- name: Cache Homebrew packages
  uses: actions/cache@v4
  with:
    path: |
      ~/Library/Caches/Homebrew
      /usr/local/Cellar
    key: ${{ runner.os }}-brew-${{ hashFiles('.github/workflows/homebrew-test.yml') }}
```

#### 6. CODEOWNERS para Formula
**Arquivo:** `.github/CODEOWNERS` (novo)

Requerer review para mudanças na formula:

```
/Formula/ @feliperbroering
/scripts/homebrew/ @feliperbroering
```

---

### Baixa Prioridade

#### 7. Consistência de Idioma
A codebase mistura português e inglês. Considerar padronizar:
- `doctor.py` usa português ("Componente", "Status das Dependências")
- Formula e docs usam inglês

#### 8. Timeout para post_install
Se manter o `doctor --setup` no post_install, adicionar timeout:

```ruby
# Timeout de 45 minutos para setup
Timeout.timeout(2700) do
  system "#{bin}/metalscribe", "doctor", "--setup"
end
```

#### 9. Workflow Manual para Release
Adicionar workflow dispatch para releases manuais:

```yaml
on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release (e.g., v0.2.0)'
        required: true
```

---

## Resumo de Ações

| Prioridade | Item | Esforço |
|------------|------|---------|
| 🔴 Alta | SHA256 real no release | 5 min |
| 🔴 Alta | Tornar doctor --setup opt-in | 15 min |
| 🔴 Alta | Corrigir verificação curl | 5 min |
| 🟡 Média | Validar formato versão | 5 min |
| 🟡 Média | Cache CI | 15 min |
| 🟡 Média | CODEOWNERS | 5 min |
| 🟢 Baixa | Consistência idioma | 30 min |
| 🟢 Baixa | Timeout post_install | 10 min |
| 🟢 Baixa | Workflow dispatch | 15 min |

---

## Referências

- [Homebrew Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/learn-github-actions/usage-limits-billing-and-administration)
- [Semantic Versioning](https://semver.org/)
