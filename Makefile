.PHONY: help docker-mongo docker-json local-mongo local-json stop clean logs \
        test-movie test-user test-booking test-schedule test-all \
        mongo-shell mongo-check logs-movie logs-user logs-booking logs-schedule logs-mongodb

# Couleurs pour le terminal
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
BLUE   := \033[0;34m
NC     := \033[0m # No Color

# ============================================================================
# AIDE
# ============================================================================
help:
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)        SYSTÈME DE MICROSERVICES - COMMANDES DISPONIBLES    $(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)LANCEMENT AVEC DOCKER :$(NC)"
	@echo "  make docker-mongo     - Lance Docker + MongoDB"
	@echo "  make docker-json      - Lance Docker + JSON"
	@echo ""
	@echo "$(YELLOW)LANCEMENT LOCAL (sans Docker) :$(NC)"
	@echo "  make local-mongo      - Lance en local + MongoDB"
	@echo "  make local-json       - Lance en local + JSON"
	@echo ""
	@echo "$(YELLOW)GESTION :$(NC)"
	@echo "  make stop             - Arrête tous les conteneurs"
	@echo "  make clean            - Supprime conteneurs + volumes + cache"
	@echo "  make logs             - Affiche les logs en temps réel"
	@echo "  make logs-movie       - Logs du service Movie"
	@echo "  make logs-user        - Logs du service User"
	@echo "  make logs-booking     - Logs du service Booking"
	@echo "  make logs-schedule    - Logs du service Schedule"
	@echo "  make logs-mongodb     - Logs de MongoDB"
	@echo ""
	@echo "$(YELLOW)TESTS :$(NC)"
	@echo "  make test-movie       - Teste le service Movie (GraphQL)"
	@echo "  make test-user        - Teste le service User (REST)"
	@echo "  make test-booking     - Teste le service Booking (GraphQL)"
	@echo "  make test-schedule    - Teste le service Schedule (gRPC)"
	@echo "  make test-all         - Teste tous les services"
	@echo ""
	@echo "$(YELLOW)MONGODB :$(NC)"
	@echo "  make mongo-shell      - Ouvre le shell MongoDB"
	@echo "  make mongo-check      - Vérifie les données dans MongoDB"
	@echo ""
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"

# ============================================================================
# DOCKER + MONGODB
# ============================================================================
docker-mongo:
	@echo "$(GREEN)🐳 Lancement Docker + MongoDB...$(NC)"
	@echo "USE_DOCKER=true" > .env
	@echo "USE_MONGODB=true" >> .env
	@cat .env.template >> .env
	@docker-compose up -d --build
	@echo ""
	@echo "$(GREEN)✓ Services démarrés !$(NC)"
	@echo "$(YELLOW)Attendez 10 secondes que MongoDB s'initialise...$(NC)"
	@sleep 10
	@echo "$(GREEN)✓ Services prêts !$(NC)"
	@echo ""
	@echo "$(BLUE)Pour tester les services, utilisez :$(NC)"
	@echo "  make test-user"
	@echo "  make test-movie"
	@echo "  make test-booking"
	@echo "  make test-schedule"
	@echo "  make test-all"

# ============================================================================
# DOCKER + JSON
# ============================================================================
docker-json:
	@echo "$(GREEN)🐳 Lancement Docker + JSON...$(NC)"
	@echo "USE_DOCKER=true" > .env
	@echo "USE_MONGODB=false" >> .env
	@cat .env.template >> .env
	@docker-compose up -d --build
	@echo ""
	@echo "$(GREEN)✓ Services démarrés !$(NC)"
	@sleep 5
	@echo "$(GREEN)✓ Services prêts !$(NC)"
	@echo ""
	@echo "$(BLUE)Pour tester les services, utilisez :$(NC)"
	@echo "  make test-user"
	@echo "  make test-movie"
	@echo "  make test-booking"
	@echo "  make test-schedule"
	@echo "  make test-all"

# ============================================================================
# LOCAL + MONGODB
# ============================================================================
local-mongo:
	@echo "$(YELLOW)⚠️  Mode local + MongoDB$(NC)"
	@echo "$(YELLOW)Prérequis : MongoDB doit être installé et démarré en local$(NC)"
	@echo ""
	@echo "USE_DOCKER=false" > .env
	@echo "USE_MONGODB=true" >> .env
	@echo "MONGO_HOST=localhost" >> .env
	@cat .env.template >> .env
	@echo "$(GREEN)Configuration créée !$(NC)"
	@echo ""
	@echo "$(YELLOW)Pour démarrer les services :$(NC)"
	@echo "  cd user && python user.py &"
	@echo "  cd movie && python movie.py &"
	@echo "  cd booking && python booking.py &"
	@echo "  cd schedule && python schedule.py &"

# ============================================================================
# LOCAL + JSON
# ============================================================================
local-json:
	@echo "$(YELLOW)⚠️  Mode local + JSON$(NC)"
	@echo ""
	@echo "USE_DOCKER=false" > .env
	@echo "USE_MONGODB=false" >> .env
	@cat .env.template >> .env
	@echo "$(GREEN)Configuration créée !$(NC)"
	@echo ""
	@echo "$(YELLOW)Pour démarrer les services :$(NC)"
	@echo "  cd user && python user.py &"
	@echo "  cd movie && python movie.py &"
	@echo "  cd booking && python booking.py &"
	@echo "  cd schedule && python schedule.py &"

# ============================================================================
# ARRÊT DES SERVICES
# ============================================================================
stop:
	@echo "$(YELLOW)🛑 Arrêt des services...$(NC)"
	@docker-compose stop
	@echo "$(GREEN)✓ Services arrêtés$(NC)"

# ============================================================================
# NETTOYAGE COMPLET
# ============================================================================
clean:
	@echo "$(RED)🗑️  Nettoyage complet...$(NC)"
	@docker-compose down -v
	@docker system prune -f
	@rm -f .env
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

# ============================================================================
# LOGS
# ============================================================================
logs:
	@docker-compose logs -f

logs-movie:
	@docker-compose logs -f movie

logs-user:
	@docker-compose logs -f user

logs-booking:
	@docker-compose logs -f booking

logs-schedule:
	@docker-compose logs -f schedule

logs-mongodb:
	@docker-compose logs -f mongodb

# ============================================================================
# TESTS - USER (REST)
# ============================================================================
test-user:
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)                     TEST SERVICE USER (REST)               $(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(BLUE)1. Health check$(NC)"
	@curl -s http://localhost:3201/health | python3 -m json.tool || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)2. Vérification admin (chris_rivers - devrait être admin)$(NC)"
	@curl -s http://localhost:3201/users/chris_rivers/is_admin | python3 -m json.tool || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)3. Vérification non-admin (peter_curley)$(NC)"
	@curl -s http://localhost:3201/users/peter_curley/is_admin | python3 -m json.tool || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)4. Récupération de tous les utilisateurs (admin)$(NC)"
	@curl -s http://localhost:3201/chris_rivers/users/json | python3 -m json.tool || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)5. Tentative de récupération par non-admin (doit échouer)$(NC)"
	@curl -s http://localhost:3201/peter_curley/users/json | python3 -m json.tool || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(GREEN)✓ Tests User terminés$(NC)"
	@echo ""

# ============================================================================
# TESTS - MOVIE (GraphQL)
# ============================================================================
test-movie:
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)                   TEST SERVICE MOVIE (GraphQL)             $(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(BLUE)1. Health check$(NC)"
	@curl -s http://localhost:3200/health | python3 -m json.tool || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)2. Récupération de tous les films (admin)$(NC)"
	@curl -s -X POST http://localhost:3200/chris_rivers/graphql \
		-H "Content-Type: application/json" \
		-d '{"query": "{ all_movies { id title director rating } }"}' \
		| python3 -m json.tool || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)3. Récupération d'un film par ID$(NC)"
	@curl -s -X POST http://localhost:3200/chris_rivers/graphql \
		-H "Content-Type: application/json" \
		-d '{"query": "{ movie_by_id(id: \"a8034f44-aee4-44cf-b32c-74cf452aaaae\") { id title director rating } }"}' \
		| python3 -m json.tool || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)4. Récupération d'un film par titre (The Martian)$(NC)"
	@curl -s -X POST http://localhost:3200/chris_rivers/graphql \
		-H "Content-Type: application/json" \
		-d '{"query": "{ movie_by_title(title: \"The Martian\") { id title director rating } }"}' \
		| python3 -m json.tool || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)5. Films par réalisateur (Ridley Scott)$(NC)"
	@curl -s -X POST http://localhost:3200/chris_rivers/graphql \
		-H "Content-Type: application/json" \
		-d '{"query": "{ movies_by_director(director: \"Ridley Scott\") { id title director rating } }"}' \
		| python3 -m json.tool || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)6. Films avec rating >= 7.0$(NC)"
	@curl -s -X POST http://localhost:3200/chris_rivers/graphql \
		-H "Content-Type: application/json" \
		-d '{"query": "{ movies_by_rating(min_rating: 7.0) { id title director rating } }"}' \
		| python3 -m json.tool || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)7. Ajout d'un film (admin)$(NC)"
	@curl -s -X POST http://localhost:3200/chris_rivers/graphql \
		-H "Content-Type: application/json" \
		-d '{"query": "mutation { add_movie(title: \"Test Movie\", director: \"Test Director\", rating: 7.5) { id title director rating } }"}' \
		| python3 -m json.tool || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)8. Tentative d'ajout par non-admin (doit échouer)$(NC)"
	@curl -s -X POST http://localhost:3200/peter_curley/graphql \
		-H "Content-Type: application/json" \
		-d '{"query": "mutation { add_movie(title: \"Unauthorized\", director: \"Test\", rating: 5.0) { id title director rating } }"}' \
		| python3 -m json.tool || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(GREEN)✓ Tests Movie terminés$(NC)"
	@echo ""

# ============================================================================
# TESTS - BOOKING (GraphQL)
# ============================================================================
test-booking:
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)                 TEST SERVICE BOOKING (GraphQL)             $(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(BLUE)1. Health check$(NC)"
	@curl -s http://localhost:3203/health | python3 -m json.tool
	@echo ""
	@echo "$(BLUE)2. Récupération de toutes les réservations (admin)$(NC)"
	@curl -s -X POST http://localhost:3203/chris_rivers/graphql \
		-H "Content-Type: application/json" \
		-d '{"query": "{ bookings_json(user_id: \"chris_rivers\") { userid { id name is_admin } dates { date movies { id title director rating } } } }"}' \
		| python3 -m json.tool
	@echo ""
	@echo "$(BLUE)3. Réservations d'un utilisateur spécifique (chris_rivers)$(NC)"
	@curl -s -X POST http://localhost:3203/chris_rivers/graphql \
		-H "Content-Type: application/json" \
		-d '{"query": "{ booking_with_id(user_id: \"chris_rivers\", id: \"chris_rivers\") { userid { id name is_admin } dates { date movies { id title director rating } } } }"}' \
		| python3 -m json.tool
	@echo ""
	@echo "$(BLUE)4. Ajout d'une réservation (admin)$(NC)"
	@curl -s -X POST http://localhost:3203/chris_rivers/graphql \
		-H "Content-Type: application/json" \
		-d "{\"query\": \"mutation { add_booking(user_id: \\\"chris_rivers\\\", userid: \\\"chris_rivers\\\", date: \\\"20151214\\\", movieid: \\\"a8034f44-aee4-44cf-b32c-74cf452aaaae\\\") { userid { id name } dates { date movies { id title } } } }\"}" \
		| python3 -m json.tool
	@echo ""
	@echo "$(GREEN)✓ Tests Booking terminés$(NC)"
	@echo ""

# ============================================================================
# TESTS - SCHEDULE (gRPC)
# ============================================================================
test-schedule:
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)                  TEST SERVICE SCHEDULE (gRPC)              $(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(BLUE)0. Vérification des dates disponibles dans MongoDB$(NC)"
	@docker exec mongodb mongosh --quiet --eval "use schedules_db; db.schedules.find({}, {date: 1, _id: 0}).limit(5).forEach(s => print('Date disponible: ' + s.date))"
	@echo ""
	@echo "$(BLUE)1. Récupération de toutes les séances (GetJson - stream)$(NC)"
	@grpcurl -plaintext \
		-import-path schedule/protos \
		-proto schedule.proto \
		-d '{"userId":"chris_rivers"}' \
		localhost:3202 Schedule/GetJson || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)2. Récupération des films pour une date (20151201)$(NC)"
	@grpcurl -plaintext \
		-import-path schedule/protos \
		-proto schedule.proto \
		-d '{"userId":"chris_rivers","date":"20151201"}' \
		localhost:3202 Schedule/GetMoviesByDate || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)3. Récupération des dates d'un film spécifique$(NC)"
	@grpcurl -plaintext \
		-import-path schedule/protos \
		-proto schedule.proto \
		-d '{"userId":"chris_rivers","movieId":"a8034f44-aee4-44cf-b32c-74cf452aaaae"}' \
		localhost:3202 Schedule/GetScheduleByMovie || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)4. Ajout d'une nouvelle séance (admin uniquement)$(NC)"
	@grpcurl -plaintext \
		-import-path schedule/protos \
		-proto schedule.proto \
		-d '{"userId":"chris_rivers","date":"20251215","moviesId":["a8034f44-aee4-44cf-b32c-74cf452aaaae"]}' \
		localhost:3202 Schedule/AddSchedule || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)5. Vérification : récupération de la nouvelle séance$(NC)"
	@grpcurl -plaintext \
		-import-path schedule/protos \
		-proto schedule.proto \
		-d '{"userId":"chris_rivers","date":"20251215"}' \
		localhost:3202 Schedule/GetMoviesByDate || echo "$(RED)✗ Échec$(NC)"
	@echo ""
	@echo "$(BLUE)6. Tentative d'ajout par non-admin (doit échouer)$(NC)"
	@grpcurl -plaintext \
		-import-path schedule/protos \
		-proto schedule.proto \
		-d '{"userId":"peter_curley","date":"20251216","moviesId":["a8034f44-aee4-44cf-b32c-74cf452aaaae"]}' \
		localhost:3202 Schedule/AddSchedule || echo "$(YELLOW)⚠️  Accès refusé (comportement attendu)$(NC)"
	@echo ""
	@echo "$(GREEN)✓ Tests Schedule terminés$(NC)"
	@echo ""

# ============================================================================
# TESTS - TOUS LES SERVICES
# ============================================================================
test-all:
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)              TESTS COMPLETS DE TOUS LES SERVICES           $(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@make test-user
	@make test-movie
	@make test-booking
	@make test-schedule
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)                  ✓ TOUS LES TESTS TERMINÉS                 $(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════$(NC)"

# ============================================================================
# MONGODB - VÉRIFICATION DES DONNÉES
# ============================================================================
mongo-shell:
	@echo "$(GREEN)🔍 Ouverture du shell MongoDB...$(NC)"
	@echo "$(YELLOW)Commandes utiles :$(NC)"
	@echo "  show dbs                    - Liste les bases"
	@echo "  use movies_db               - Sélectionne une base"
	@echo "  show collections            - Liste les collections"
	@echo "  db.movies.find().pretty()   - Affiche les films"
	@echo "  exit                        - Quitter"
	@echo ""
	@docker exec -it mongodb mongosh

mongo-check:
	@echo "$(GREEN)🔍 Vérification des données MongoDB...$(NC)"
	@echo ""
	@echo "$(BLUE)📊 Base: users_db$(NC)"
	@docker exec mongodb mongosh --quiet --eval "use users_db; print('Nombre d\\'utilisateurs: ' + db.users.countDocuments()); db.users.find().limit(2).forEach(u => print('- ' + u.name + ' (admin: ' + u.is_admin + ')'))"
	@echo ""
	@echo "$(BLUE)🎬 Base: movies_db$(NC)"
	@docker exec mongodb mongosh --quiet --eval "use movies_db; print('Nombre de films: ' + db.movies.countDocuments()); db.movies.find().limit(3).forEach(m => print('- ' + m.title + ' par ' + m.director + ' (' + m.rating + '/10)'))"
	@echo ""
	@echo "$(BLUE)📅 Base: schedules_db$(NC)"
	@docker exec mongodb mongosh --quiet --eval "use schedules_db; print('Nombre de dates: ' + db.schedules.countDocuments()); db.schedules.find().limit(2).forEach(s => print('- Date: ' + s.date + ' (' + s.movies.length + ' films)'))"
	@echo ""
	@echo "$(BLUE)🎟️  Base: bookings_db$(NC)"
	@docker exec mongodb mongosh --quiet --eval "use bookings_db; print('Nombre de réservations: ' + db.bookings.countDocuments()); db.bookings.find().limit(2).forEach(b => print('- User: ' + b.userid + ' (' + b.dates.length + ' dates)'))"
	@echo ""
	@echo "$(GREEN)✓ Vérification terminée$(NC)"