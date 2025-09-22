CREATE TABLE IF NOT EXISTS CLIENT (
    ID_CLIENT SERIAL PRIMARY KEY,
    EMAIL VARCHAR(100) UNIQUE NOT NULL,
    USERNAME VARCHAR(50) UNIQUE NOT NULL,
    PASSWORD_HASH VARCHAR(255) NOT NULL,
    PHOTO BYTEA,
    SEX CHAR(1) CHECK (SEX IN ('M','F')),
    DATE_BIRTH DATE
);

CREATE TABLE IF NOT EXISTS PRODUCT (
    ID_PRODUCT SERIAL PRIMARY KEY,
    NAME_PRODUCT VARCHAR(100),
    GENRE VARCHAR(50),
    PLATFORM VARCHAR(200),
    GAME_MODE VARCHAR(200),
    PRICE NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS RATING (
    ID_CLIENT INT REFERENCES CLIENT(ID_CLIENT),
    ID_PRODUCT INT,
    RATING INT CHECK (RATING BETWEEN 1 AND 5),
    PRIMARY KEY (ID_CLIENT, ID_PRODUCT)
);


INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Spider-Man: Miles Morales', 'Ação / Aventura', 'PlayStation', 'Single-player, Mundo Aberto', 130.84);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Hollow Knight: Silksong', 'Metroidvania / Ação', 'PC, Nintendo Switch', 'Single-player', 167.84);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Tomb Raider', 'Ação / Aventura', 'PC, PlayStation, Xbox', 'Single-player', 176.51);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Stray', 'Aventura / Puzzle', 'PC, PlayStation', 'Single-player', 68.63);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Terraria', 'Aventura / Sandbox', 'PC, PlayStation, Xbox, Nintendo Switch, Mobile', 'Single-player, Multiplayer online, Cooperativo', 132.90);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Minecraft', 'Sandbox / Sobrevivência', 'PC, PlayStation, Xbox, Nintendo Switch, Mobile', 'Single-player, Multiplayer online, Cooperativo', 70.95);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Call of Duty', 'FPS / Ação', 'PC, PlayStation, Xbox', 'Single-player, Multiplayer online, Competitivo', 95.74);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Red Dead Redemption', 'Ação / Aventura', 'PlayStation, Xbox', 'Single-player, Mundo Aberto, Multiplayer online', 93.37);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Until Dawn', 'Horror / Narrativo', 'PlayStation', 'Single-player', 35.14);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('God of War', 'Ação / Aventura', 'PC, PlayStation', 'Single-player, Mundo Aberto', 99.94);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Ghost of Tsushima', 'Ação / Aventura', 'PlayStation', 'Single-player, Mundo Aberto, Cooperativo (Legends Mode)', 76.40);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Life Is Strange', 'Aventura narrativa', 'PC, PlayStation, Xbox, Nintendo Switch', 'Single-player', 65.28);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Overcooked', 'Party Game / Estratégia', 'PC, PlayStation, Xbox, Nintendo Switch', 'Cooperativo local, Multiplayer', 193.35);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('It Takes Two', 'Plataforma / Puzzle', 'PC, PlayStation, Xbox', 'Cooperativo obrigatório', 67.24);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('The Cult of the Lamb', 'Roguelike / Simulação', 'PC, PlayStation, Xbox, Nintendo Switch', 'Single-player', 182.92);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Stardew Valley', 'Simulação / RPG', 'PC, PlayStation, Xbox, Nintendo Switch, Mobile', 'Single-player, Multiplayer online, Cooperativo', 155.57);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Castlevania', 'Metroidvania / Ação', 'Multiplataforma (dependendo da versão)', 'Single-player', 121.15);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('The Pedestrian', 'Puzzle / Plataforma', 'PC, PlayStation, Xbox, Nintendo Switch', 'Single-player', 159.74);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Anno Mutationem', 'Ação / RPG', 'PC, PlayStation', 'Single-player', 118.99);

INSERT INTO PRODUCT (NAME_PRODUCT, GENRE, PLATFORM, GAME_MODE, PRICE)
VALUES ('Shadow of the Colossus', 'Ação / Aventura', 'PlayStation', 'Single-player', 130.31);

/* Média das avaliações */
SELECT p.NAME_PRODUCT, AVG(r.RATING) AS media_rating
FROM PRODUCT p
LEFT JOIN RATING r ON p.ID_PRODUCT = r.ID_PRODUCT
GROUP BY p.NAME_PRODUCT
ORDER BY media_rating DESC;

/* Avaliações de um cliente em específico */
SELECT p.NAME_PRODUCT, r.RATING
FROM RATING r
JOIN PRODUCT p ON r.ID_PRODUCT = p.ID_PRODUCT
JOIN CLIENT c ON r.ID_CLIENT = c.ID_CLIENT
WHERE c.USERNAME = 'user51';