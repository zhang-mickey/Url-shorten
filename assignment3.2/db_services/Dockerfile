# Use the official PostgreSQL image as the base
FROM postgres:15

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=123456
ENV POSTGRES_DB=WSCBS_assignment

# Copy custom initialization scripts (optional)
#COPY init.sql /docker-entrypoint-initdb.d/

# Expose PostgreSQL port
EXPOSE 5432

# Run PostgreSQL
CMD ["postgres"]