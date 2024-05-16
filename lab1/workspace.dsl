workspace {
    name "Серивис доставки"

    !identifiers hierarchical


    model {

        properties { 
            structurizr.groupSeparator "/"
        }

        user = person "Пользователь"

        deliver_system = softwareSystem "Сервис доставки" {
            description "Сервис доставки"

            
            user_service = container "User service" {
                description "Сервис управления пользователями"
            } 

            deliver_service = container "Deliver service" {
                description "Сервис создания и отслеживания доставки"
            } 
            
            order_service = container "Order service" {
                description "Сервис создания и отслеживания посылок"
            } 

            group "Слой данных" {
                user_database = container "User database" {
                    description "База данных пользоватей"
                    technology "PostgreSQL 15"
                    tags "database"
                }

                deliver_database = container "Deliver database" {
                    description "База данных доставок"
                    technology "MongoDB 5"
                    tags "database"
                }

                order_database = container "Order database" {
                    description "База данных посылок"
                    technology "MongoDB 5"
                    tags "database"
                }
            }

            user -> user_service "Регистрация и авторизация пользователей"
            user -> deliver_service "Создание доставки, получение информации о доставке"
            user -> order_service "Создание посылки и получение информации о посылке"

            user_service -> user_database "Получение и изменение данных о пользователях"

            deliver_service -> order_service "Получение информации о доставке"
			deliver_service -> deliver_database "Получение и изменение данных о доставках"
            deliver_service -> user_service "Информация о получателях и отправителях"

			order_service -> order_database "Хранеине информации о посылках"
  
        }

        user -> deliver_system "Создание доставки и получение инфомации о доставке"

    }
    
    views {
        themes default

        properties {
            structurizr.tooltips true
        }

        systemContext deliver_system {
            autoLayout
            include *
        }

        container deliver_system {
            autoLayout
            include *
        }

        dynamic deliver_system "UC01" "Создание нового пользователя" {
            autoLayout
            user -> deliver_system.user_service "Создание пользователя (POST /user)"
            deliver_system.user_service -> deliver_system.user_database "Сохранение данных о пользователе" 
        }

        dynamic deliver_system "UC02" "Поиск пользователя по логину" {
            autoLayout
            user -> deliver_system.user_service "Поиск пользователя (GET /user)"
            deliver_system.user_service -> deliver_system.user_database "Получение данных о пользователе из БД"
        }

        dynamic deliver_system "UC03" "Поиск пользователя по маске имени и фамилии" {
            autoLayout
            user -> deliver_system.user_service "Поиск пользователя"
            deliver_system.user_service -> deliver_system.user_database "Получение данных о пользователях, соответствующих маске"
        }

        dynamic deliver_system "UC04" "Добавить посылку" {
            autoLayout
            user -> deliver_system.user_service "Аунтефикация пользователя"
            user -> deliver_system.order_service "Создание новой посылки (POST /task)"
            deliver_system.order_service -> deliver_system.order_database "Сохранение посылки"
        }

        dynamic deliver_system "UC05" "Получение посылок пользователя" {
            autoLayout
            user -> deliver_system.user_service "Аунтефикация пользователя"
            user -> deliver_system.order_service "Получение списка всех посылок пользователя (GET /task)"
            deliver_system.order_service -> deliver_system.order_database "Получение всех посылок из БД"
        }

        dynamic deliver_system "UC06" "Создание доставки от пользователя к пользователю" {
            autoLayout
            user -> deliver_system.user_service "Аунтефикация пользователя"
            user -> deliver_system.deliver_service "Создание доставки (POST /order)"
		 	deliver_system.deliver_service -> deliver_system.user_service "Информация о получателе"
		 	deliver_system.deliver_service -> deliver_system.order_service "Информация о посылке"
            deliver_system.deliver_service -> deliver_system.deliver_database "Создание доставки"
        }
        
        dynamic deliver_system "UC07" "Получение информации о доставке по получателю" {
            autoLayout
            user -> deliver_system.deliver_service "Получение информации о доставке по получателю (GET /order)"
            deliver_system.deliver_service -> deliver_system.deliver_database "Получение информации о посылке (GET /order)"
        }

        dynamic deliver_system "UC08" "Получение информации о доставке по отправителю" {
            autoLayout
            user -> deliver_system.deliver_service "Получение информации о доставке по отправителю (GET /order)"
            deliver_system.deliver_service -> deliver_system.deliver_database "Получение информации о посылке (GET /order)"
        }

        styles {
            element "database" {
                shape cylinder
            }
        }
    }
}