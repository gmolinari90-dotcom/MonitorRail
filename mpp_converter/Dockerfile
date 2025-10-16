FROM eclipse-temurin:17-jdk-jammy
WORKDIR /app
COPY target/monitorrail-mpp-converter-0.1.0.jar /app/app.jar
EXPOSE 8080
ENTRYPOINT ["java","-Xms512m","-Xmx1g","-jar","/app/app.jar"]

