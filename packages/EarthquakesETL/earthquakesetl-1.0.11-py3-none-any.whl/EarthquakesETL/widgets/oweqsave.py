import Orange
from AnyQt.QtWidgets import QComboBox
from AnyQt.QtCore import Qt
from datetime import datetime

from Orange.data import Table
from Orange.data.sql.backend import Backend
from Orange.data.sql.backend.base import BackendError
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.utils.itemmodels import PyListModel
from Orange.widgets.utils.owbasesql import OWBaseSql
from Orange.widgets.utils.sql import check_sql_input
from Orange.widgets.widget import Msg, OWWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QGridLayout, QLineEdit, QPushButton, QSizePolicy, QLabel, QRadioButton, QCheckBox, \
    QHBoxLayout
from orangewidget.utils.signals import Input
import Orange.data.pandas_compat as pc

from sqlalchemy import create_engine

import bcrypt

MAX_DL_LIMIT = 1000000


def is_postgres(backend):
    return getattr(backend, 'display_name', '') == "PostgreSQL"


class BackendModel(PyListModel):
    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if role == Qt.DisplayRole:
            return self[row].display_name
        return super().data(index, role)


class oweqsave(OWBaseSql, OWWidget):
    name = "EQ Save"
    description = "Save a dataset into a DB."
    icon = "icons/EQSave.png"
    priority = 2250
    keywords = "sql table, save, data, db, dataset"

    class Inputs:
        data = Input("Dataset", Orange.data.Table)
        config_catalog = Input("Catalog Config", Orange.data.Table)
        config_dataset = Input("Dataset Config", Orange.data.Table)
        config_decluster = Input("Declustering Config", Orange.data.Table)
        catalog = Input("Catalog", Orange.data.Table)

    class Outputs:
        pass

    settings_version = 2
    buttons_area_orientation = None
    selected_backend = Setting(None)
    sql = Setting("")

    class Warning(OWBaseSql.Warning):
        missing_extension = Msg("Database is missing extensions: {}")

    class Error(OWBaseSql.Error):
        no_backends = Msg("Please install a backend to use this widget.")
        config = Msg("There must be a configuration table.")
        config_decluster = Msg("There must be a declustered configuration table if declustered was selected.")
        catalog = Msg("There are no catalogs in the database.")
        declustered_checked = Msg("There is not a declustered configuration table")
        user_empty = Msg("You must fill in the username to log in.")
        pass_empty = Msg("You must fill in the password to log in.")


    def __init__(self):
        self.backends = None
        self.backendcombo = None
        self.data = None
        self.config_catalog = None
        self.config_dataset = None
        self.config_decluster = None
        self.catalog = None
        self.rows = 0
        self.cols = 0
        self.target = None
        self.logged = 0
        self.catalogname = ""
        self.datasetname = ""
        self.idConfig_catalog = None
        self.idConfig_dataset = None
        super().__init__()

    def update_labels(self):
        if self.b1.isChecked():
            self.rows_label.setText("Rows: " + str(self.rows))
            self.cols_label.hide()
            self.target_label.hide()
        else:
            self.rows_label.setText("Rows: " + str(self.rows))
            self.cols_label.setText("Columns: " + str(self.cols))
            self.target_label.setText("Class: " + str(self.target))
            self.cols_label.show()
            self.target_label.show()

    @Inputs.config_catalog
    def setConfig_catalog(self, config_catalog=None):
        self.config_catalog = config_catalog

    @Inputs.config_dataset
    def setConfig_dataset(self, config_dataset=None):
        self.config_dataset = config_dataset

    @Inputs.catalog
    def setCatalog(self, catalog=None):
        self.catalog = catalog
        if self.catalog is not None:
            self.rows = len(self.catalog)
            self.cols = len(self.catalog.domain)
            self.update_labels()

    @Inputs.config_decluster
    def setConfig_decluster(self, config_decluster=None):
        self.config_decluster = config_decluster


    @Inputs.data
    @check_sql_input
    def setData(self, data=None):
        self.data = data
        target_variable = ""
        if self.data is not None:
            self.rows = len(self.data)
            self.cols = len(self.data.domain)
            target_variable = self.data.domain.class_var
        else:
            self.rows = 0
            self.cols = 0
            self.target = "None"
        if target_variable is not None:
            if isinstance(target_variable, Orange.data.DiscreteVariable):
                self.target = "categorical"
            if isinstance(target_variable, Orange.data.ContinuousVariable):
                self.target = "numeric"
        else:
            self.target = None

        self.update_labels()

    def _setup_gui(self):
        super()._setup_gui()
        layoutB = QGridLayout()
        layoutB.setSpacing(4)

        # Caja principal
        box = gui.widgetBox(self.controlArea, orientation=layoutB, box='Login/Register')

        self.usuario = QLineEdit(placeholderText="User...", toolTip="User")
        layoutB.addWidget(self.usuario, 0, 0, 1, 2)

        self.userpass = QLineEdit(placeholderText="Password...", toolTip="Password")
        self.userpass.setEchoMode(QLineEdit.Password)
        layoutB.addWidget(self.userpass, 1, 0, 1, 2)

        self.btn_loginregister = QPushButton("Login/Register", toolTip="Login / Register",
                                             minimumWidth=120)
        self.btn_loginregister.clicked.connect(self.login_register)

        self.label_logged = QLabel("Logged!!")
        self.label_logged.hide()

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.btn_loginregister)
        h_layout.addStretch()
        h_layout.addWidget(self.label_logged)

        layoutB.addLayout(h_layout, 2, 0, 1, 2)

        layoutA = QGridLayout()
        layoutA.setSpacing(3)
        gui.widgetBox(self.controlArea, orientation=layoutA, box='Save dataset')
        self.target_label = QLabel()
        self.target_label.setText("Class: None")
        layoutA.addWidget(self.target_label, 0, 0)
        self.rows_label = QLabel()
        self.rows_label.setText("Rows: 0")
        layoutA.addWidget(self.rows_label, 1, 0)
        self.cols_label = QLabel()
        self.cols_label.setText("Columns: 0")
        layoutA.addWidget(self.cols_label, 2, 0)

        self.label_type = QLabel()
        self.label_type.setText("Type:")
        layoutA.addWidget(self.label_type, 0, 2)

        self.b1 = QRadioButton("Catalog")
        self.b1.setChecked(True)
        self.b1.toggled.connect(lambda: self.btnstate(self.b1))
        layoutA.addWidget(self.b1, 1, 2)

        self.declustered = QCheckBox("Declustered")
        layoutA.addWidget(self.declustered, 1, 3)

        self.b2 = QRadioButton("Dataset")
        self.b2.toggled.connect(lambda: self.btnstate(self.b2))

        self.catalogLabel = QLabel("Catalog:", self.controlArea)
        layoutA.addWidget(self.catalogLabel, 3, 0)
        self.catalogCombo = QComboBox(self.controlArea)
        self.catalogCombo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layoutA.addWidget(self.catalogCombo, 3, 1)

        self.catalogLabel.hide()
        self.catalogCombo.hide()

        self.catalogMessageLabel = QLabel("Logged user has no catalogs yet.", self.controlArea)
        layoutA.addWidget(self.catalogMessageLabel, 4, 0, 1, 2)
        self.catalogMessageLabel.hide()

        layoutA.addWidget(self.b2, 2, 2)
        self.setLayout(layoutA)

        self.btn_savedata = QPushButton(
            "Save", toolTip="Save a dataset into a DB",
            minimumWidth=120
        )
        self.btn_savedata.clicked.connect(self.saveData)
        self.btn_savedata.setDisabled(True)
        layoutA.addWidget(self.btn_savedata, 3, 2, alignment=Qt.AlignCenter)

        self._add_backend_controls()

    def btnstate(self, b):
        if self.catalog is not None:
            self.catalogCombo.hide()
            self.catalogLabel.hide()
            self.catalogMessageLabel.hide()
        else:
            if b == self.b1:  # Opción Catalog
                if b.isChecked():
                    self.declustered.show()
                    self.catalogCombo.hide()
                    self.catalogLabel.hide()
                    self.catalogMessageLabel.hide()
            elif b == self.b2:  # Opción Dataset
                if b.isChecked():
                    self.declustered.hide()
                    self.refresh_catalog_combo()
                else:
                    self.catalogCombo.hide()
                    self.catalogLabel.hide()
                    self.catalogMessageLabel.hide()

        self.update_labels()

    def _add_backend_controls(self):
        box = self.serverbox
        self.backends = BackendModel(Backend.available_backends())
        self.backendcombo = QComboBox(box)
        if self.backends:
            self.backendcombo.setModel(self.backends)
            names = [backend.display_name for backend in self.backends]
            if self.selected_backend and self.selected_backend in names:
                self.backendcombo.setCurrentText(self.selected_backend)
        else:
            self.Error.no_backends()
            box.setEnabled(False)
        self.backendcombo.currentTextChanged.connect(self.__backend_changed)
        box.layout().insertWidget(0, self.backendcombo)

    def __backend_changed(self):
        backend = self.get_backend()
        self.selected_backend = backend.display_name if backend else None
        self.backend = backend  # Asignamos el backend a self.backend

    def create_master_tables(self):
        query_users = f"""
        CREATE TABLE IF NOT EXISTS users
        (
            id SERIAL NOT NULL,
            usuario character varying(30) NOT NULL,
            password character varying(60) NOT NULL,
            CONSTRAINT users_pkey PRIMARY KEY (id),
            CONSTRAINT users_usuario_key UNIQUE (usuario)
        )
        """
        try:
            with self.backend.execute_sql_query(query_users):
                pass
        except BackendError as ex:
            self.Error.connection(str(ex))

        query_config_catalog = f"""
        CREATE TABLE IF NOT EXISTS catalogs_config
        (
            id SERIAL NOT NULL,
            start_date date NOT NULL,
            end_date date NOT NULL,
            min_mag real NOT NULL DEFAULT 0,
            geo_type boolean NOT NULL,
            min_lat real NOT NULL,
            max_lat real,
            min_lon real NOT NULL,
            max_lon real,
            radius real,
            declustered boolean NOT NULL,
            declustered_method boolean,
            param1 real,
            param2 real,
            param3 real,
            data_source varchar NOT NULL,
            CONSTRAINT catalogs_config_pkey PRIMARY KEY (id)
        )
        """
        try:
            with self.backend.execute_sql_query(query_config_catalog):
                pass
        except BackendError as ex:
            self.Error.connection(str(ex))

        query_catalog = f"""
        CREATE TABLE IF NOT EXISTS catalogs
        (
            id SERIAL NOT NULL,
            datetime timestamp without time zone NOT NULL,
            id_user integer NOT NULL,
            id_config integer NOT NULL,
            CONSTRAINT catalogs_pkey PRIMARY KEY (id),
            CONSTRAINT "FK_config_id" FOREIGN KEY (id_config)
                REFERENCES public.catalogs_config (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION
                NOT VALID,
            CONSTRAINT "FK_user_id" FOREIGN KEY (id_user)
                REFERENCES public.users (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION
                NOT VALID
        )
        """
        try:
            with self.backend.execute_sql_query(query_catalog):
                pass
        except BackendError as ex:
            self.Error.connection(str(ex))

        query_config_datasets = f"""
        CREATE TABLE IF NOT EXISTS datasets_config
        (
            id SERIAL NOT NULL,
            start_date timestamp without time zone NOT NULL,
            end_date timestamp without time zone NOT NULL,
            nmorales real NOT NULL,
            nadeli real NOT NULL,
            reference_magnitude real NOT NULL,
            dayspred real NOT NULL,
            class_from real NOT NULL,
            class_to real NOT NULL,
            class_step real NOT NULL,
            chth real NOT NULL,
            output_type character varying NOT NULL,
            CONSTRAINT datasets_config_pkey PRIMARY KEY (id)
        )
        """
        try:
            with self.backend.execute_sql_query(query_config_datasets):
                pass
        except BackendError as ex:
            self.Error.connection(str(ex))

        query_datasets = f"""
        CREATE TABLE IF NOT EXISTS datasets
        (
            id SERIAL NOT NULL,
            datetime timestamp without time zone NOT NULL,
            id_catalog integer NOT NULL,
            id_config integer NOT NULL,
            CONSTRAINT datasets_pkey PRIMARY KEY (id),
            CONSTRAINT "FK_catalog_id" FOREIGN KEY (id_catalog)
                REFERENCES public.catalogs (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION
                NOT VALID,
            CONSTRAINT "FK_config_id" FOREIGN KEY (id_config)
                REFERENCES public.datasets_config (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION
                NOT VALID
        )
        """
        try:
            with self.backend.execute_sql_query(query_datasets):
                pass
        except BackendError as ex:
            self.Error.connection(str(ex))

    def login_register(self):
        self.create_master_tables()
        usuario_input = str(self.usuario.text())
        password_input = str(self.userpass.text())
        if not usuario_input.strip():  # Verifica si está vacío o solo tiene espacios
            self.Error.user_empty()
            return
        if not password_input.strip():  # Verifica si está vacío o solo tiene espacios
            self.Error.pass_empty()
            return

        query_check = "SELECT id, password FROM users WHERE usuario=%s"
        try:
            with self.backend.execute_sql_query(query_check, (usuario_input,)) as cursor:
                resultado = cursor.fetchone()
        except BackendError as ex:
            self.Error.connection(str(ex))
            return

        if resultado is None:
            # Usuario no existe: se crea el usuario con contraseña hasheada
            hashed_password = bcrypt.hashpw(password_input.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            query_insert = "INSERT INTO users (usuario, password) VALUES (%s, %s) RETURNING id"
            try:
                with self.backend.execute_sql_query(query_insert, (usuario_input, hashed_password)) as cursor:
                    nuevo_id = cursor.fetchone()[0]
                    print("Usuario creado exitosamente. ID:", nuevo_id)
                    self.logged = nuevo_id
                    self.label_logged.show()
                    self.btn_loginregister.setDisabled(True)
                    self.btn_savedata.setDisabled(False)
            except BackendError as ex:
                self.Error.connection(str(ex))
                return
        else:
            # El usuario existe: se valida la contraseña usando bcrypt.checkpw
            db_id, db_password = resultado
            if not bcrypt.checkpw(password_input.encode('utf-8'), db_password.encode('utf-8')):
                print("Error: Contraseña no válida.")
                return
            else:
                print("Inicio de sesión exitoso. ID:", db_id)
                self.logged = db_id
                self.label_logged.show()
                self.btn_loginregister.setDisabled(True)
                self.btn_savedata.setDisabled(False)

        self.refresh_catalog_combo()
        return self.logged

    def get_sqlalchemy_engine(self):
        host = self.servertext.text()
        database = self.databasetext.text()
        port = 5432
        username = self.usernametext.text()
        password = self.passwordtext.text()
        conn_str = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        return create_engine(conn_str)

    def create_table_catalog(self, table_name):
        self.progressBarInit()
        try:
            df = pc.table_to_frame(self.catalog)

            if 'index' in df.columns:
                df = df.drop('index', axis=1)

        except Exception as ex:
            self.Error.connection("Error al convertir la tabla a DataFrame: " + str(ex))
            self.progressBarFinished()
            return

        if self.catalog.domain.class_var is not None:
            class_col = self.catalog.domain.class_var.name
            if class_col in df.columns:
                df = df[[class_col] + [col for col in df.columns if col != class_col]]

        try:
            # Si el backend no tiene engine, lo creamos manualmente
            if hasattr(self.backend, "engine"):
                engine = self.backend.engine
            else:
                engine = self.get_sqlalchemy_engine()
            df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        except Exception as ex:
            self.Error.connection("Error al insertar datos con pandas to_sql: " + str(ex))

        self.progressBarFinished()

    def create_table_dataset(self, table_name):
        self.progressBarInit()
        try:
            df = pc.table_to_frame(self.data, include_metas=True)
        except Exception as ex:
            self.Error.connection("Error al convertir la tabla a DataFrame: " + str(ex))
            self.progressBarFinished()
            return

        import pandas as pd

        for var in self.data.domain.attributes + self.data.domain.metas:
            if isinstance(var, Orange.data.TimeVariable):
                colname = var.name
                if colname in df.columns:
                    df[colname] = pd.to_datetime(df[colname], unit='s', errors='coerce')

        if self.data.domain.class_var is not None:
            class_col = self.data.domain.class_var.name
            if class_col in df.columns:
                df = df[[class_col] + [col for col in df.columns if col != class_col]]

        try:
            # Si el backend no dispone de un engine, se crea manualmente
            if hasattr(self.backend, "engine"):
                engine = self.backend.engine
            else:
                engine = self.get_sqlalchemy_engine()
            df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        except Exception as ex:
            self.Error.connection("Error al insertar datos con pandas to_sql: " + str(ex))

        self.progressBarFinished()

    def saveData(self):
        self.clear()

        if self.logged == 0:
            self.Error.connection("Log in or create an user")
        elif self.servertext.text() == "" or self.databasetext.text() == "":
            self.Error.connection("Host and database fields must be filled.")
        elif self.declustered.isChecked() and self.config_decluster is None:
            self.Error.config_decluster()
        else:
            self.insert_data()

    def insert_config_catalog(self, start_date, end_date, min_mag, geo_type, max_lon, max_lat, min_lon, min_lat, radius,
                              declustered, declustered_method, param1, param2, param3, data_source):
        new_start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        new_end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        query = f"""
            INSERT INTO public.catalogs_config
            (start_date, end_date, min_mag, geo_type, max_lon, max_lat, min_lon, min_lat, radius, declustered, declustered_method, 
             param1, param2, param3, data_source)
            VALUES ('{new_start_date}', '{new_end_date}', {min_mag}, {geo_type}, {max_lon.replace('nan', 'null')}, {max_lat.replace('nan', 'null')},
                    {min_lon}, {min_lat}, {radius.replace('nan', 'null')}, {declustered}, {declustered_method},
                    {param1}, {param2}, {param3.replace('nan', 'null')}, {data_source}) RETURNING id;
        """

        try:
            with self.backend.execute_sql_query(query) as cursor:
                config_id = cursor.fetchone()[0]
            return config_id
        except BackendError as ex:
            self.Error.connection(str(ex))

    def insert_config_dataset(self, start_date, end_date, nmorales, nadeli, reference_magnitude, dayspred, class_from,
                              class_step, class_to, chth, output_type):
        from datetime import datetime
        new_start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        new_end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        query = f"""
            INSERT INTO public.datasets_config
            (start_date, end_date, nmorales, nadeli, reference_magnitude, dayspred,
             class_from, class_step, class_to, chth, output_type)
            VALUES ('{new_start_date}', '{new_end_date}', {nmorales}, {nadeli}, {reference_magnitude}, {dayspred},
                    {class_from}, {class_step}, {class_to}, {chth}, '{output_type}')
            RETURNING id;
        """


        try:
            with self.backend.execute_sql_query(query) as cursor:
                new_id = cursor.fetchone()[0]
            return new_id
        except BackendError as ex:
            self.Error.connection(str(ex))

    def insert_catalog(self, idConfig_catalog):
        query = (
                "INSERT INTO public.catalogs (datetime, id_user, id_config) "
                "VALUES ('" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
                "','" + str(self.logged) +
                "','" + str(idConfig_catalog) + "') RETURNING id;"
        )
        try:
            with self.backend.execute_sql_query(query) as cursor:
                catalog_id = cursor.fetchone()[0]
            return catalog_id
        except BackendError as ex:
            self.Error.connection(str(ex))

    def insert_dataset(self, idConfig_dataset=None, idCatalog=None):
        query = "INSERT INTO public.datasets (datetime, id_catalog, id_config) VALUES ('" + datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S') + "','" + str(idCatalog) + "','" + str(idConfig_dataset) + "') RETURNING id;"
        try:
            with self.backend.execute_sql_query(query) as cursor:
                dataset_id = cursor.fetchone()[0]
            return dataset_id
        except BackendError as ex:
            self.Error.connection(str(ex))
            return

    def insert_data(self):
        if self.declustered.isChecked() and self.config_decluster is None:
            self.Error.declustered_checked()
        if self.config_catalog is not None:
            df_catalog_config = pc.table_to_frame(self.config_catalog, include_metas=True)
            if self.b1.isChecked() and self.declustered.isChecked():
                df_config_decluster = pc.table_to_frame(self.config_decluster, include_metas=True)
                self.idConfig_catalog = self.insert_config_catalog(str(df_catalog_config.loc[0, 'Start Date']),
                    str(df_catalog_config.loc[0, 'End Date']), str(df_catalog_config.loc[0, 'Magnitude']), True if
                    (df_catalog_config.loc[0, 'Place'] == 'Rectangle') else False, 'null' if
                    (df_catalog_config.loc[0, 'Max Longitude'] is None or str(df_catalog_config.loc[0, 'Max Longitude']) == 'None')
                    else str(df_catalog_config.loc[0, 'Max Longitude']), 'null' if (df_catalog_config.loc[0, 'Max Latitude']
                    is None or str(df_catalog_config.loc[0, 'Max Latitude']) == 'None') else str(df_catalog_config.loc[0, 'Max Latitude']),
                    str(df_catalog_config.loc[0, 'Min Longitude']), str(df_catalog_config.loc[0, 'Min Latitude']), 'null' if
                    (df_catalog_config.loc[0, 'Max Radius Km'] is None or str(df_catalog_config.loc[0, 'Max Radius Km']) == 'None')
                    else str(df_catalog_config.loc[0, 'Max Radius Km']), True, True if (df_config_decluster.loc[0, 'Declustering Method'] == 'Gardner-Knopoff')
                    else False, str(df_config_decluster.loc[0, 'Param1']), str(df_config_decluster.loc[0, 'Param2']),
                    'null' if (df_config_decluster.loc[0, 'Param3'] is None or str(df_config_decluster.loc[0, 'Param3']) == 'None')
                    else str(df_config_decluster.loc[0, 'Param3']), "'"+str(df_catalog_config.loc[0, 'Data Source']+"'"))

            elif self.b1.isChecked():
                self.idConfig_catalog = self.insert_config_catalog(str(df_catalog_config.loc[0, 'Start Date']), str(df_catalog_config.loc[0, 'End Date']),
                    str(df_catalog_config.loc[0, 'Magnitude']), True if (df_catalog_config.loc[0, 'Place'] == 'Rectangle') else False,
                    'null' if (df_catalog_config.loc[0, 'Max Longitude'] is None or str(df_catalog_config.loc[0, 'Max Longitude']) == 'None')
                    else str(df_catalog_config.loc[0, 'Max Longitude']), 'null' if (df_catalog_config.loc[0, 'Max Latitude'] is None or
                    str(df_catalog_config.loc[0, 'Max Latitude']) == 'None')else str(df_catalog_config.loc[0, 'Max Latitude']),
                    str(df_catalog_config.loc[0, 'Min Longitude']), str(df_catalog_config.loc[0, 'Min Latitude']),
                    'null' if (df_catalog_config.loc[0, 'Max Radius Km'] is None or str(df_catalog_config.loc[0, 'Max Radius Km']) == 'None')
                    else str(df_catalog_config.loc[0, 'Max Radius Km']), False, 'null', 'null', 'null', 'null', "'" +
                    str(df_catalog_config.loc[0, 'Data Source']+"'"))

        if self.b1.isChecked():
            self.idCatalog = self.insert_catalog(self.idConfig_catalog)

        if self.b2.isChecked():
            if self.catalog is None:
                df_config_dataset = pc.table_to_frame(self.config_dataset, include_metas=True)
                selected_catalog_id = self.catalogCombo.currentText()
                print(selected_catalog_id)
                self.idCatalog = selected_catalog_id
                self.idConfig_dataset = self.insert_config_dataset(str(df_config_dataset.loc[0, 'Start Date']), str(df_config_dataset.loc[0, 'End Date']),
                                str(df_config_dataset.loc[0, 'Events for b-value Morales']), str(df_config_dataset.loc[0, 'Events for b-value Adeli']),
                                str(df_config_dataset.loc[0, 'Reference Magnitude']), str(df_config_dataset.loc[0, 'Prediction Days']),
                                str(df_config_dataset.loc[0, 'Classification From']), str(df_config_dataset.loc[0, 'Classification Step']),
                                str(df_config_dataset.loc[0, 'Classification To']), str(df_config_dataset.loc[0, 'Threshold (mu and c)']),
                                str(df_config_dataset.loc[0, 'Output Type']))
                self.idDataset = self.insert_dataset(self.idConfig_dataset, selected_catalog_id.split("_")[1])
                if selected_catalog_id is None:
                    self.Error.catalog()
            else:
                if self.declustered.isChecked():
                    df_config_decluster = pc.table_to_frame(self.config_decluster, include_metas=True)
                    self.idConfig_catalog = self.insert_config_catalog(str(df_catalog_config.loc[0, 'Start Date']), str(df_catalog_config.loc[0, 'End Date']),
                                str(df_catalog_config.loc[0, 'Magnitude']), True if (df_catalog_config.loc[0, 'Place'] == 'Rectangle') else False,
                                'null' if (df_catalog_config.loc[0, 'Max Longitude'] is None or str(df_catalog_config.loc[0, 'Max Longitude']) == 'None')
                                else str(df_catalog_config.loc[0, 'Max Longitude']), 'null' if (df_catalog_config.loc[0, 'Max Latitude'] is None or
                                str(df_catalog_config.loc[0, 'Max Latitude']) == 'None') else str(df_catalog_config.loc[0, 'Max Latitude']),
                                str(df_catalog_config.loc[0, 'Min Longitude']), str(df_catalog_config.loc[0, 'Min Latitude']), 'null' if
                                (df_catalog_config.loc[0, 'Max Radius Km'] is None or str(df_catalog_config.loc[0, 'Max Radius Km']) == 'None')
                                else str(df_catalog_config.loc[0, 'Max Radius Km']), True, True if (df_config_decluster.loc[ 0, 'Declustering Method']
                                == 'Gardner-Knopoff') else False, str(df_config_decluster.loc[0, 'Param1']), str(df_config_decluster.loc[0, 'Param2']),
                                'null' if (df_config_decluster.loc[0, 'Param3'] is None or str(df_config_decluster.loc[0, 'Param3']) == 'None')
                                else str(df_config_decluster.loc[0, 'Param3']),"'" + str(df_catalog_config.loc[0, 'Data Source'] + "'"))
                else:
                    self.idConfig_catalog = self.insert_config_catalog(str(df_catalog_config.loc[0, 'Start Date']), str(df_catalog_config.loc[0, 'End Date']),
                                str(df_catalog_config.loc[0, 'Magnitude']), True if (df_catalog_config.loc[0, 'Place'] == 'Rectangle') else False,
                                'null' if (df_catalog_config.loc[0, 'Max Longitude'] is None or str(df_catalog_config.loc[0, 'Max Longitude']) == 'None')
                                else str(df_catalog_config.loc[0, 'Max Longitude']), 'null' if (df_catalog_config.loc[0, 'Max Latitude'] is None or
                                str(df_catalog_config.loc[0, 'Max Latitude']) == 'None') else str(df_catalog_config.loc[0, 'Max Latitude']),
                                str(df_catalog_config.loc[0, 'Min Longitude']), str(df_catalog_config.loc[0, 'Min Latitude']), 'null' if
                                (df_catalog_config.loc[0, 'Max Radius Km'] is None or str(df_catalog_config.loc[0, 'Max Radius Km']) == 'None')
                                else str(df_catalog_config.loc[0, 'Max Radius Km']), False, 'null', 'null', 'null', 'null', "'" +
                                str(df_catalog_config.loc[0, 'Data Source'] + "'"))

                self.idCatalog = self.insert_catalog(self.idConfig_catalog)

                df_config_dataset = pc.table_to_frame(self.config_dataset, include_metas=True)
                self.idConfig_dataset = self.insert_config_dataset(str(df_config_dataset.loc[0, 'Start Date']), str(df_config_dataset.loc[0, 'End Date']),
                                                                   str(df_config_dataset.loc[0, 'Events for b-value Morales']),
                                                                   str(df_config_dataset.loc[0, 'Events for b-value Adeli']),
                                                                   str(df_config_dataset.loc[0, 'Reference Magnitude']),
                                                                   str(df_config_dataset.loc[0, 'Prediction Days']),
                                                                   str(df_config_dataset.loc[0, 'Classification From']),
                                                                   str(df_config_dataset.loc[0, 'Classification Step']),
                                                                   str(df_config_dataset.loc[0, 'Classification To']),
                                                                   str(df_config_dataset.loc[0, 'Threshold (mu and c)']),
                                                                   str(df_config_dataset.loc[0, 'Output Type']))
                self.idDataset = self.insert_dataset(self.idConfig_dataset, self.idCatalog)

        if self.b1.isChecked():
            self.catalogname = f"catalog_{self.idCatalog}"
            self.create_table_catalog(str(self.catalogname))
        else:
            if self.catalog is None:
                self.datasetname = f"dataset_{self.idDataset}"
                self.create_table_dataset(str(self.datasetname))
            else:
                self.catalogname = f"catalog_{self.idCatalog}"
                self.datasetname = f"dataset_{self.idDataset}"
                self.create_table_catalog(str(self.catalogname))
                self.create_table_dataset(str(self.datasetname))

    def user_catalogs(self):
        if self.backend is None:
            return []
        print("Usuario logueado:", self.logged)
        query = "SELECT c.id FROM catalogs c JOIN users u ON c.id_user = u.id WHERE c.id_user = %s ORDER BY c.datetime DESC"
        try:
            with self.backend.execute_sql_query(query, (self.logged,)) as cursor:
                resultados = cursor.fetchall()
        except BackendError as ex:
            self.Error.connection(str(ex))
            return []
            # Extraemos el primer elemento de cada tupla (el ID del catálogo)
        return [fila[0] for fila in resultados]

    def refresh_catalog_combo(self):
        if self.catalog is not None:
            self.catalogCombo.hide()
            self.catalogLabel.hide()
            self.catalogMessageLabel.hide()
        else:
            catalog_ids = self.user_catalogs()
            self.catalogCombo.clear()
            for cat_id in catalog_ids:
                self.catalogCombo.addItem("catalog_" + str(cat_id))
            if self.b2.isChecked():
                if not catalog_ids:
                    self.catalogCombo.hide()
                    self.catalogLabel.hide()
                    if self.logged != 0:
                        self.catalogMessageLabel.show()
                else:
                    self.catalogMessageLabel.hide()
                    self.catalogLabel.show()
                    self.catalogCombo.show()
            else:
                self.catalogCombo.hide()
                self.catalogLabel.hide()
                self.catalogMessageLabel.hide()

    def highlight_error(self, text=""):
        err = ['', 'QLineEdit {border: 2px solid red;}']
        self.servertext.setStyleSheet(err['server' in text or 'host' in text])
        self.usernametext.setStyleSheet(err['role' in text])
        self.databasetext.setStyleSheet(err['database' in text])

    def get_backend(self):
        if self.backendcombo.currentIndex() < 0:
            return None
        return self.backends[self.backendcombo.currentIndex()]

    def on_connection_success(self):
        super().on_connection_success()
        self.connectbutton.setStyleSheet("background-color: green; color: white;")
        QTimer.singleShot(1000, self.reset_boton)

    def reset_boton(self):
        self.connectbutton.setStyleSheet("")

    def on_connection_error(self, err):
        super().on_connection_error(err)
        self.highlight_error(str(err).split("\n")[0])
        self.connectbutton.setStyleSheet("background-color: red; color: white;")
        QTimer.singleShot(1000, self.reset_boton)

    def clear(self):
        self.Error.connection.clear()
        self.highlight_error()

    @classmethod
    def migrate_settings(cls, settings, version):
        if version < 2:
            # Until Orange version 3.4.4 username and password had been stored
            # in Settings.
            cm = cls._credential_manager(settings["host"], settings["port"])
            cm.username = settings["username"]
            cm.password = settings["password"]
