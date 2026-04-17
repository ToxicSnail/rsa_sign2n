# rsa_sign2n

Набор инструментов для атаки на JWT через подмену алгоритма. По двум JWT-токенам, подписанным RS256/RS384/RS512, инструмент восстанавливает RSA публичный ключ и подделывает новые токены с подписью HS256 - без предварительного знания публичного ключа.

## Алгоритм работы

1. Вы перехватываете два JWT-токена, подписанных RS256, от целевого сервера.
2. Инструмент вычисляет RSA публичный ключ (модуль `n`) через НОД двух выражений, построенных по подписям.
3. Кандидаты на публичный ключ сохраняются как `.pem`-файлы.
4. Подделанный JWT переподписывается алгоритмом HS256, где секрет - восстановленный публичный ключ.
5. Если сервер принимает HS256 и использует тот же ключ, поддельный токен пройдёт проверку.

Атака эксплуатирует класс уязвимостей, при которых сервер принимает и RS256, и HS256, не разграничивая алгоритм при валидации.

## Быстрый старт

Проще всего запустить через Docker или `uv`. Подробности — в [standalone/README.md](standalone/README.md).

**Через uv:**
```bash
# Установка зависимостей
curl -LsSf https://astral.sh/uv/install.sh | sh
sudo apt install build-essential libffi-dev libgmp-dev libmpfr-dev libmpc-dev

# Запуск
uv run standalone/jwt_forgery.py <jwt_token_1> <jwt_token_2>
```

**Через Docker:**
```bash
cd standalone
sudo docker compose build
sudo docker run --rm -it -v "$(pwd):/app" sig2n
# Внутри контейнера:
uv run jwt_forgery.py <jwt_token_1> <jwt_token_2>
```

Инструмент выведет все варианты поддельных JWT. Попробуйте каждый против цели — один из них должен сработать.

Если нужно переподписать токен с другим payload (например, другой `sub` или `role`) — используйте второй шаг:

```bash
uv run standalone/forge_from_pem.py <key.pem> \
  --payload '{"sub":"admin","exp":9999999999}' \
  --header '{"kid":"your-key-id"}'
```

## Структура репозитория

| Путь | Описание |
|------|----------|
| `standalone/jwt_forgery.py` | Основной скрипт атаки — восстанавливает ключ и подделывает JWT |
| `standalone/forge_from_pem.py` | Подделка JWT с произвольным payload из уже готового PEM-файла |
| `sig2n.py` | Прототип низкого уровня: восстановление RSA-модуля из двух пар сообщение/подпись |
| `CVE-2017-11424/` | PoC для уязвимости подмены алгоритма в pyJWT (RS256 → HS256) |
| `CVE-2016-10555/` | PoC для той же уязвимости в Node.js-библиотеке `jwt-simple` |

## CVE

- **CVE-2017-11424** — pyJWT принимал HS256-токены, где секретом служила строка публичного ключа, что позволяло подделать токен при наличии ключа.
- **CVE-2016-10555** — та же проблема в Node.js-библиотеке `jwt-simple`.

Данный инструмент идёт дальше: он работает даже тогда, когда публичный ключ заранее неизвестен — восстанавливая его из подписанных токенов.

## Ссылки

- [Abusing JWT Public Keys Without the Public Key](https://blog.silentsignal.eu/2021/02/08/abusing-jwt-public-keys-without-the-public-key/) — разбор от Silent Signal
- [Recovering RSA modulus from signatures](https://crypto.stackexchange.com/questions/30289/is-it-possible-to-recover-an-rsa-modulus-from-its-signatures/30301#30301) — математика за `sig2n.py`
