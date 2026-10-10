#!/usr/bin/env bash

# ==============================================================================
# Script de Teste da API NBA Hangman via cURL
# Certifique-se de que a API está rodando (./mvnw spring-boot:run na pasta ./nba)
# ==============================================================================

BASE_URL="http://localhost:8080"
USERNAME="lebron_fan_$RANDOM"
PASSWORD="securepassword123"
DELAY=1.5 # Intervalo em segundos entre cada requisição

echo "============================================================"
echo " 1. Registrando novo usuário: $USERNAME"
echo "============================================================"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

echo "Resposta: $REGISTER_RESPONSE"
echo ""

# Extrai o token JWT da resposta
TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "Erro: Não foi possível obter o token de autenticação. A API está rodando?"
  exit 1
fi

echo ">> Token JWT obtido com sucesso!"
echo ">> Aguardando ${DELAY}s..."
sleep "$DELAY"
echo ""

echo "============================================================"
echo " 2. Realizando Login com o usuário criado"
echo "============================================================"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

echo "Resposta: $LOGIN_RESPONSE"
echo ">> Aguardando ${DELAY}s..."
sleep "$DELAY"
echo ""

echo "============================================================"
echo " 3. Criando nova partida (Dificuldade: 1=Easy, Categoria: 1=Champion)"
echo "============================================================"
NEW_GAME_RESPONSE=$(curl -s -X POST "$BASE_URL/api/games" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"difficulty": 1, "category": 1}')

echo "Resposta: $NEW_GAME_RESPONSE"
echo ""

# Extrai o gameId
GAME_ID=$(echo "$NEW_GAME_RESPONSE" | grep -o '"gameId":"[^"]*' | cut -d'"' -f4)

if [ -z "$GAME_ID" ]; then
  echo "Erro: Não foi possível extrair o gameId."
  exit 1
fi

echo ">> Partida iniciada com ID: $GAME_ID"
echo ">> Aguardando ${DELAY}s..."
sleep "$DELAY"
echo ""

echo "============================================================"
echo " 4. Enviando palpite da letra 'A'"
echo "============================================================"
GUESS_1=$(curl -s -X POST "$BASE_URL/api/games/$GAME_ID/guess" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"guess": "A"}')

echo "Resposta: $GUESS_1"
echo ">> Aguardando ${DELAY}s..."
sleep "$DELAY"
echo ""

echo "============================================================"
echo " 5. Enviando palpite repetido da letra 'A' (não deve perder vida)"
echo "============================================================"
GUESS_REPEAT=$(curl -s -X POST "$BASE_URL/api/games/$GAME_ID/guess" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"guess": "A"}')

echo "Resposta: $GUESS_REPEAT"
echo ">> Aguardando ${DELAY}s..."
sleep "$DELAY"
echo ""

echo "============================================================"
echo " 6. Enviando palpite de letra que provavelmente não existe: 'Z'"
echo "============================================================"
GUESS_WRONG=$(curl -s -X POST "$BASE_URL/api/games/$GAME_ID/guess" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"guess": "Z"}')

echo "Resposta: $GUESS_WRONG"
echo ">> Aguardando ${DELAY}s..."
sleep "$DELAY"
echo ""

echo "============================================================"
echo " 7. Consultando o estado atual da partida via GET"
echo "============================================================"
GET_GAME=$(curl -s -X GET "$BASE_URL/api/games/$GAME_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "Resposta: $GET_GAME"
echo ">> Aguardando ${DELAY}s..."
sleep "$DELAY"
echo ""

echo "============================================================"
echo " 8. Consultando o Leaderboard / Scoreboard"
echo "============================================================"
SCOREBOARD=$(curl -s -X GET "$BASE_URL/api/scoreboard")

echo "Resposta: $SCOREBOARD"
echo ""

echo "============================================================"
echo " Testes concluídos com sucesso!"
echo "============================================================"
