db-run:
	docker run --rm  --name  db_mc855_authenticator -p 5940:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=1234 -e POSTGRES_DB=db_mc855_authenticator -d postgres

db-stop:
	docker stop postgres

db-shell:
	docker exec -it postgres psql -U postgres

