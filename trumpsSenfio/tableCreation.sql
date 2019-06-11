drop table eventos;
drop table locais;
drop table funcionario;

create table funcionario (
	id integer AUTO_INCREMENT,
    nome varchar(40) UNIQUE,
    constraint funcionario_pk PRIMARY KEY (id)
);

create table locais (
	id integer AUTO_INCREMENT,
    nomeLocal varchar(20) UNIQUE,
    constraint locais_pk PRIMARY KEY (id)
);

create table eventos (
	idEvento integer AUTO_INCREMENT,
    evento varchar(6) NOT NULL,
	idFuncionario integer NOT NULL,
    idLocal integer NOT NULL,
    dataHora datetime NOT NULL,
    CONSTRAINT eventos_pk PRIMARY KEY (idEvento),
    CONSTRAINT funcionario_fk FOREIGN KEY (idFuncionario) REFERENCES funcionario(id),
    CONSTRAINT locais_fk FOREIGN KEY (idLocal) REFERENCES locais(id)
);