
startDb:
	docker run --name mysqldb -e MYSQL_ROOT_PASSWORD=password -it -p 6603:3306 mysql

build:
	docker build . --tag app:v1

run:
	docker run -d -p 5000:5000 --name appcontainer1 --link mysqldb:mysql app:v1
	