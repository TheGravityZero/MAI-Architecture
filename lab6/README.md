# Лабораторная работа 6
## Circuit Breaker
### Цель
Получение практических навыков в построении отказоустойчивых приложений.


### Задание
Необходимо реализовать сервис API Gateway, который будет получать JWT токен в User Service и вызывать сервисы согласно варианту задания.
Для вызова сервисов, согласно варианту задания реализовать паттерн Circuit Breaker.

## Запуск:
```
docker compose up

# пересобрать
docker compose up --build
```
```
# API Swagger
localhost:8080/docs
```
## Зайти в базу:
```
docker exec -it postgres /bin/bash
psql -U root -d postgres
```