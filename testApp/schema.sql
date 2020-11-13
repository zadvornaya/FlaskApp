DROP TABLE IF EXISTS Testing;
DROP TABLE IF EXISTS Answers;
DROP TABLE IF EXISTS Questions;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
    userID INTEGER PRIMARY KEY AUTOINCREMENT,
    login VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    name VARCHAR,
    surname VARCHAR,
    dateOfBirth DATE,
    progress INTEGER(2) DEFAULT 0
);

CREATE TABLE Questions (
    quesID INTEGER PRIMARY KEY AUTOINCREMENT,
    quesCont TEXT UNIQUE NOT NULL
);

CREATE TABLE Answers (
    ansID INTEGER PRIMARY KEY AUTOINCREMENT,
    quesID INTEGER REFERENCES Questions (quesID) ON DELETE CASCADE,
    ansCont TEXT NOT NULL,
    validity BOOLEAN NOT NULL
);

CREATE TABLE Testing (
    userID INTEGER REFERENCES Users (userID) ON DELETE CASCADE,
    quesID INTEGER REFERENCES Questions (quesID) ON DELETE CASCADE,
    ansID INTEGER REFERENCES Answers (ansID) ON DELETE CASCADE,
    answered TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT name_unique UNIQUE (userID, quesID, ansID)
);

INSERT INTO Questions (quesCont) VALUES
    ("Основной недостаток Data-Mining:"),
    ("Графические элементы DFD:"),
    ("Информационный ... - это процесс, в который вовлечены отправитель и получатель, соединенные надежным каналом связи с целью передачи информации."),
    ("Отличительной особенностью метода моделирования бизнес-процессов IDEF0 является:"),
    ("Обширный подраздел искусственного интеллекта, математическая дисциплина, использующая разделы математической статистики, численных методов оптимизации, теории вероятностей, дискретного анализа, и извлекающая знания из данных.");

INSERT INTO Answers (quesID, ansCont, validity) VALUES
    (1, "жесткая зависимость результата анализа от репрезентативности первоначальной информации", 1),
    (1, "зависимость применяемого алгоритма анализа от характера данных в хранилище данных", 0),
    (1, "необходимость в наличии больших объемов данных", 0),

    (2, "перекрестки", 0),
    (2, "потоки данных", 1),
    (2, "хранилища данных", 1),
    (2, "потоки функций", 0),
    (2, "зоны ответственности", 0),

    (3, "обмен", 1),

    (4, "расположение работ в порядке доминирования", 1),
    (4, "цветное отображение объектов", 0),
    (4, "отражение объектов, предназначенных для хранения информации", 0),
    (4, "использование иерархии диаграмм", 1),
    (4, "описание цепочки процесса управляемого события", 0),

    (5, "Machine Learning", 1),
    (5, "Big Data", 0),
    (5, "Data-mining", 0);
