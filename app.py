# -----------------------------------------------------------------------
# 0. IMPORTACIONES
# -----------------------------------------------------------------------
import streamlit as st              # Interfaz web
import pandas as pd                 # Manipulación de datos
import io, xlsxwriter               # Archivos binarios / Excel
from datetime import datetime       # Fechas
import pytz                         # Zona horaria Lima

# -----------------------------------------------------------------------
# 1. CONFIGURACIÓN GENERAL
# -----------------------------------------------------------------------
st.set_page_config(page_title="Magest App", page_icon="🤰")
st.title("🤰 Magest App")
st.markdown("---")

# -----------------------------------------------------------------------
# 2. DICCIONARIOS Y LISTAS DE REFERENCIA
# -----------------------------------------------------------------------

# --- Mapeo de código → nombre del centro ---
CENTRO_MAP = {
    "478": "CAP III ALFREDO PIAZZA ROBERTS",
    "446": "CAP III EL AGUSTINO",
    "447": "CAP III HUAYCAN",
    "481": "CAP III INDEPENDENCIA",
    "019": "CENTRO MEDICO ANCIJE",
    "020": "CENTRO MEDICO CASAPALCA",
    "406": "HOSPITAL I AURELIO DIAZ UFANO Y PERAL",
    "404": "HOSPITAL I JORGE VOTO BERNALLES CORPANCHO",
    "403": "HOSPITAL II CLINICA GERIATRICA SAN ISIDRO LABRADOR",
    "017": "HOSPITAL II RAMON CASTILLA",
    "008": "HOSPITAL II VITARTE",
    "007": "HOSPITAL III EMERGENCIAS GRAU",
    "011": "POLICLINICO CHOSICA",
    "376": "POLICLINICO DE COMPLEJIDAD CRECIENTE SAN LUIS",
    "014": "POLICLINICO FRANCISCO PIZARRO",
    "023": "POSTA MEDICA CONSTRUCCION CIVIL",
    "002": "RED PRESTACIONAL ALMENARA",
}

# --- Columnas esperadas ---
columnas_explota = [
    "CENTRO", "PERIODO", "SERVICIO", "ACTIVIDAD", "SUBACTIVIDAD", "DOC_PROFESIONAL",
    "PROFESIONAL", "FECHA_ATENCION", "DOC_PACIENTE", "PACIENTE", "EDAD", "TEL_MOVIL",
    "FECHA_SOLIC", "FECHA_CITA", "DES_DIAGNOSTICO", "TIPODIAG", "TIPO_GRAVIDEZ",
    "CASODIAG", "N_R_C_SER", "RESULT_ATENCION"
]

columnas_citas = [
    "CENTRO", "PERIODO", "SERVICIO", "ACTIVIDAD", "SUBACTIVIDAD",
    "FECHA_SOLIC", "FECHA_CITA", "HORA_CITA", "CONDICION_CITA", "ESTADO_CITA",
    "TIPO_CITA", "H_C", "DOC_PROFESIONAL", "PROFESIONAL", "TIPO_PACIENTE",
    "DOC_PACIENTE", "PACIENTE", "FECNACIMPACIENTE", "EDAD", "SEXO",
    "TEL_MOVIL", "CAS_ADSCRIPCION", "N_R_C_SER", "N_R_C_EST", "TURNO",
    "DESCONSULTORIO", "OBSERVACION"
]

cols_show_explota = columnas_explota.copy()
cols_show_citas   = columnas_citas.copy()

# .....................................................................
# Mapeo alternativo por palabras (completo, sin omisiones)
# .....................................................................
CENTRO_MAP_RESULT_FINAL = {
    "Alfredo": "CAP III ALFREDO PIAZZA ROBERTS",
    "Piazza": "CAP III ALFREDO PIAZZA ROBERTS",
    "Roberts": "CAP III ALFREDO PIAZZA ROBERTS",
    "El": "CAP III EL AGUSTINO",
    "Agustino": "CAP III EL AGUSTINO",
    "Huaycan": "CAP III HUAYCAN",
    "Independencia": "CAP III INDEPENDENCIA",
    "Ancije": "CENTRO MEDICO ANCIJE",
    "Casapalca": "CENTRO MEDICO CASAPALCA",
    "Aurelio": "HOSPITAL I AURELIO DIAZ UFANO Y PERAL",
    "Diaz": "HOSPITAL I AURELIO DIAZ UFANO Y PERAL",
    "Ufano": "HOSPITAL I AURELIO DIAZ UFANO Y PERAL",
    "Peral": "HOSPITAL I AURELIO DIAZ UFANO Y PERAL",
    "Jorge": "HOSPITAL I JORGE VOTO BERNALLES CORPANCHO",
    "Voto": "HOSPITAL I JORGE VOTO BERNALLES CORPANCHO",
    "Bernalles": "HOSPITAL I JORGE VOTO BERNALLES CORPANCHO",
    "Corpancho": "HOSPITAL I JORGE VOTO BERNALLES CORPANCHO",
    "Clinica": "HOSPITAL II CLINICA GERIATRICA SAN ISIDRO LABRADOR",
    "Geriatrica": "HOSPITAL II CLINICA GERIATRICA SAN ISIDRO LABRADOR",
    "Isidro": "HOSPITAL II CLINICA GERIATRICA SAN ISIDRO LABRADOR",
    "Labrador": "HOSPITAL II CLINICA GERIATRICA SAN ISIDRO LABRADOR",
    "Ramon": "HOSPITAL II RAMON CASTILLA",
    "Castilla": "HOSPITAL II RAMON CASTILLA",
    "Vitarte": "HOSPITAL II VITARTE",
    "Emergencias": "HOSPITAL III EMERGENCIAS GRAU",
    "Grau": "HOSPITAL III EMERGENCIAS GRAU",
    "Chosica": "POLICLINICO CHOSICA",
    "De": "POLICLINICO DE COMPLEJIDAD CRECIENTE SAN LUIS",
    "Complejidad": "POLICLINICO DE COMPLEJIDAD CRECIENTE SAN LUIS",
    "Creciente": "POLICLINICO DE COMPLEJIDAD CRECIENTE SAN LUIS",
    "Luis": "POLICLINICO DE COMPLEJIDAD CRECIENTE SAN LUIS",
    "Francisco": "POLICLINICO FRANCISCO PIZARRO",
    "Pizarro": "POLICLINICO FRANCISCO PIZARRO",
    "Posta": "POSTA MEDICA CONSTRUCCION CIVIL",
    "Medica": "POSTA MEDICA CONSTRUCCION CIVIL",
    "Construccion": "POSTA MEDICA CONSTRUCCION CIVIL",
    "Civil": "POSTA MEDICA CONSTRUCCION CIVIL",
    "Red": "RED PRESTACIONAL ALMENARA",
    "Prestacional": "RED PRESTACIONAL ALMENARA",
    "Almenara": "RED PRESTACIONAL ALMENARA"
}

# --- Mapeo de nombres equivalentes de columnas ---
nombres_equivalentes = {
    "APENOMB_MEDICO": "PROFESIONAL",
    "TELEF_MOVIL": "TEL_MOVIL",
    "DOC_MEDICO": "DOC_PROFESIONAL",
    "DNI_MEDICO": "DOC_PROFESIONAL",
    "DESC_DIAGNOSTICO": "DES_DIAGNOSTICO",
    "TIPO_DIAG": "TIPODIAG",
    "CASO_DIAG": "CASODIAG",
    "DNI": "DOC_PACIENTE",
    "ANNOS": "EDAD"
}

# --- Nombres de meses en español ---
meses_es = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# -----------------------------------------------------------------------
# 3. FUNCIONES DE UTILIDAD
# -----------------------------------------------------------------------
def mes_es(fecha_str: str) -> str:
    """Convierte una cadena de fecha al nombre del mes en español."""
    fecha = pd.to_datetime(fecha_str, dayfirst=True, errors="coerce")
    if pd.isna(fecha):
        fecha = pd.to_datetime(fecha_str, errors="coerce")
    return meses_es.get(fecha.month, "") if not pd.isna(fecha) else ""

def non_empty_count(row: pd.Series) -> int:
    """Cuenta celdas no vacías en la fila."""
    return row.replace("", pd.NA).notna().sum()

def nombre_archivo(seccion: str, extension: str) -> str:
    """Genera nombre de archivo con timestamp (horario Lima)."""
    lima = pytz.timezone("America/Lima")
    ahora = datetime.now(lima)
    return f"{seccion}_{ahora.strftime('%Y%m%d_%H%M')}.{extension}"

def aplicar_centro_map_contains(texto: str) -> str:
    """Devuelve el nombre completo del centro si el texto contiene palabras clave."""
    for palabra, nombre_completo in CENTRO_MAP_RESULT_FINAL.items():
        if pd.notna(texto) and palabra.upper() in texto.upper():
            return nombre_completo
    return texto

def estandarizar_dataframe(df: pd.DataFrame, columnas_objetivo: list[str]) -> pd.DataFrame:
    """Reordena y completa columnas faltantes con ''. """
    df = df.reindex(columns=columnas_objetivo, fill_value="")
    return df[columnas_objetivo]

# -----------------------------------------------------------------------
# 4. ESTADO UI
# -----------------------------------------------------------------------
for key, default in {
    "show_explota": False,
    "show_citas": False
}.items():
    st.session_state.setdefault(key, default)

# =======================================================================
# 5. SECCIÓN 1 – EXPLOTA MATCH
# =======================================================================
st.header("📂 Explota Match")
explota_files = st.file_uploader(
    "Sube uno o más archivos .txt para Explota Match",
    type=["txt"], accept_multiple_files=True, key="explota"
)

df_total_explota = pd.DataFrame()
if explota_files:
    dfs_explota = []
    for f in explota_files:
        try:
            df = pd.read_csv(f, sep="|", dtype=str, keep_default_na=False, encoding="utf-8")
            df.columns = df.columns.str.strip()
            df.rename(columns=nombres_equivalentes, inplace=True)
            if "TIPODIAG" in df.columns:
                df["TIPODIAG"] = df["TIPODIAG"].replace({"P": "PRESUNTIVO", "D": "DEFINITIVO"})
            df["CENTRO"] = df["CENTRO"].map(CENTRO_MAP).fillna(df["CENTRO"])
            dfs_explota.append(estandarizar_dataframe(df, columnas_explota))
        except Exception as e:
            st.error(f"Error en {f.name}: {e}")

    if dfs_explota:
        df_total_explota = pd.concat(dfs_explota, ignore_index=True)
        st.success("Explota cargado ✅")

        col_view, col_txt, col_xlsx = st.columns(3)
        with col_view:
            if st.button("👁️ Ver/Ocultar Explota", key="tgl_explota"):
                st.session_state.show_explota = not st.session_state.show_explota
        with col_txt:
            if st.button("📥 Descargar Explota TXT", key="exp_txt_btn"):
                with st.spinner("Generando TXT..."):
                    txt_exp_bytes = df_total_explota.to_csv(
                        sep="|", index=False, lineterminator="\n"
                    ).encode("utf-8")
                st.download_button(
                    "⬇️ Haz click para bajar TXT",
                    txt_exp_bytes,
                    file_name=nombre_archivo("explota", "txt"),
                    mime="text/plain",
                    key="exp_txt_dl"
                )
        with col_xlsx:
            if st.button("📥 Descargar Explota Excel", key="exp_xlsx_btn"):
                with st.spinner("Generando Excel..."):
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                        df_total_explota.to_excel(writer, index=False, sheet_name="Explota")
                    data_xlsx = buf.getvalue()
                st.download_button(
                    "⬇️ Haz click para bajar Excel",
                    data_xlsx,
                    file_name=nombre_archivo("explota", "xlsx"),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="exp_xlsx_dl"
                )

        if st.session_state.show_explota:
            st.write(f"Total filas: {len(df_total_explota)}")
            st.dataframe(df_total_explota[cols_show_explota])

# =======================================================================
# 6. SECCIÓN 2 – CITAS MÉDICAS
# =======================================================================
st.markdown("---")
st.header("📋 Citas Médicas")
citas_files = st.file_uploader(
    "Sube uno o más archivos .txt para Citas Médicas",
    type=["txt"], accept_multiple_files=True, key="citas"
)

df_citas = pd.DataFrame()
if citas_files:
    dfs_citas = []
    for f in citas_files:
        try:
            df = pd.read_csv(f, sep="|", dtype=str, keep_default_na=False, encoding="utf-8")
            df.columns = df.columns.str.strip()
            df.rename(columns=nombres_equivalentes, inplace=True)
            if "TIPODIAG" in df.columns:
                df["TIPODIAG"] = df["TIPODIAG"].replace({"P": "PRESUNTIVO", "D": "DEFINITIVO"})
            df["CENTRO"] = df["CENTRO"].map(CENTRO_MAP).fillna(df["CENTRO"])
            dfs_citas.append(estandarizar_dataframe(df, columnas_citas))
        except Exception as e:
            st.error(f"Error en {f.name}: {e}")

    if dfs_citas:
        df_citas = pd.concat(dfs_citas, ignore_index=True)
        st.success("Citas cargado ✅")

        col_view, col_txt, col_xlsx = st.columns(3)
        with col_view:
            if st.button("👁️ Ver/Ocultar Citas", key="tgl_citas"):
                st.session_state.show_citas = not st.session_state.show_citas
        with col_txt:
            if st.button("📥 Descargar Citas TXT", key="cit_txt_btn"):
                with st.spinner("Generando TXT..."):
                    txt_cit_bytes = df_citas.to_csv(
                        sep="|", index=False, lineterminator="\n"
                    ).encode("utf-8")
                st.download_button(
                    "⬇️ Haz click para bajar TXT",
                    txt_cit_bytes,
                    file_name=nombre_archivo("citas", "txt"),
                    mime="text/plain",
                    key="cit_txt_dl"
                )
        with col_xlsx:
            if st.button("📥 Descargar Citas Excel", key="cit_xlsx_btn"):
                with st.spinner("Generando Excel..."):
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                        df_citas.to_excel(writer, index=False, sheet_name="Citas")
                    data_xlsx = buf.getvalue()
                st.download_button(
                    "⬇️ Haz click para bajar Excel",
                    data_xlsx,
                    file_name=nombre_archivo("citas", "xlsx"),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="cit_xlsx_dl"
                )

        if st.session_state.show_citas:
            st.write(f"Total filas: {len(df_citas)}")
            st.dataframe(df_citas[cols_show_citas].reset_index(drop=True))

# =======================================================================
# 7. SECCIÓN 3 – RESULTADO FINAL
# =======================================================================
st.markdown("---")
st.header("📊 Resultado final")

if not df_total_explota.empty and not df_citas.empty:
    if st.button("⚙️ Generar resultado final", key="btn_generar"):

        # --- 7.1 Filtrar grupos con Medicina General & Obstetra ---
        req_serv = {"MEDICINA GENERAL", "OBSTETRA"}
        tmp_cit = df_citas.copy()
        tmp_cit["SERVICIO_UP"] = tmp_cit["SERVICIO"].str.upper()
        grupos_ok = (
            tmp_cit.groupby(["DOC_PACIENTE", "PACIENTE", "FECHA_CITA"])["SERVICIO_UP"]
            .apply(lambda s: req_serv.issubset(set(s))).reset_index(name="flag")
        )
        grupos_ok = grupos_ok[grupos_ok["flag"]].drop(columns="flag")

        # --- 7.2 Seleccionar registros de citas / explota ---
        df_cit_sel = df_citas.merge(
            grupos_ok, on=["DOC_PACIENTE", "PACIENTE", "FECHA_CITA"], how="inner"
        )
        df_cit_sel["DOC_PACIENTE_citas"] = df_cit_sel["DOC_PACIENTE"]
        df_cit_sel["FECHA_SOLIC_citas"]  = df_cit_sel["FECHA_SOLIC"]
        df_cit_sel["FECHA_CITA_citas"]   = df_cit_sel["FECHA_CITA"]

        df_expl_sel = df_total_explota.merge(
            grupos_ok[["DOC_PACIENTE", "PACIENTE", "FECHA_CITA"]],
            on=["DOC_PACIENTE", "PACIENTE"], how="inner"
        )

        alt_cols = [c for c in df_expl_sel.columns if c.startswith("FECHA_CITA")]
        if "FECHA_CITA" not in df_expl_sel.columns and alt_cols:
            df_expl_sel["FECHA_CITA"] = df_expl_sel[alt_cols[0]]

        # --- 7.3 Columnas *_match ---
        df_expl_sel["FECHA_SOLIC_match"] = df_expl_sel["FECHA_SOLIC"]
        df_expl_sel["FECHA_CITA_match"]  = df_expl_sel["FECHA_CITA"]

        # --- 7.4 Enriquecer y renombrar ---
        df_expl_sel["MES_match"] = df_expl_sel["FECHA_ATENCION"].apply(mes_es)
        df_cit_sel ["MES_citas"] = df_cit_sel ["FECHA_CITA"].apply(mes_es)

        df_expl_sel = df_expl_sel.rename(columns={
            "SERVICIO": "SERVICIO_match",
            "DOC_PROFESIONAL": "DNI_MEDICO_match",
            "PROFESIONAL": "PROFESIONAL_match",
        })
        df_cit_sel = df_cit_sel.rename(columns={
            "SERVICIO": "SERVICIO_citas",
            "DOC_PROFESIONAL": "DNI_MEDICO_citas",
            "PROFESIONAL": "PROFESIONAL CITA",
        })

        # --- 7.5 Llaves de servicio ----------
        df_expl_sel["SERVICIO_KEY"] = df_expl_sel["SERVICIO_match"].str.upper()
        df_cit_sel ["SERVICIO_KEY"] = df_cit_sel ["SERVICIO_citas"].str.upper()

        # Mantener solo una cita por combinación paciente-fecha-servicio
        df_cit_sel["_idx"] = df_cit_sel.groupby(
            ["DOC_PACIENTE", "PACIENTE", "FECHA_CITA", "SERVICIO_KEY"]
        ).cumcount()
        df_cit_first = df_cit_sel[df_cit_sel["_idx"] == 0].drop(columns="_idx")

        # --- 7.6 Merge Explota ⇄ Cita principal ---
        merged = df_expl_sel.merge(
            df_cit_first,
            on=["DOC_PACIENTE", "PACIENTE", "FECHA_CITA", "SERVICIO_KEY"],
            how="left", suffixes=("", "_y")
        )
        merged["FECHA_SOLIC"] = merged["FECHA_SOLIC_citas"]
        merged["FECHA_CITA"]  = merged["FECHA_CITA_citas"]

        # --- 7.7 Citas remanentes (“rojas”) ---
        used_keys = merged[["DOC_PACIENTE", "PACIENTE", "FECHA_CITA", "SERVICIO_KEY"]]
        df_cit_rest = df_cit_sel.merge(
            used_keys.drop_duplicates(),
            on=["DOC_PACIENTE", "PACIENTE", "FECHA_CITA", "SERVICIO_KEY"],
            how="left", indicator=True
        )
        df_cit_rest = df_cit_rest[df_cit_rest["_merge"] == "left_only"].drop(columns=["_merge"])

        rojo_cols = [
            "CENTRO", "PERIODO", "DOC_PACIENTE", "PACIENTE", "EDAD", "TEL_MOVIL",
            "SERVICIO_match", "ACTIVIDAD", "SUBACTIVIDAD", "MES_match",
            "FECHA_ATENCION", "DNI_MEDICO_match", "PROFESIONAL_match",
            "FECHA_SOLIC_match", "FECHA_CITA_match"
        ]
        for c in rojo_cols:
            df_cit_rest[c] = ""

        # --- 7.8 Concatenar y ordenar preliminar ---
        merged["orden"] = 0
        df_cit_rest["orden"] = 1
        df_res = (
            pd.concat([merged, df_cit_rest], ignore_index=True)
              .sort_values(by=["DOC_PACIENTE", "FECHA_CITA_citas", "orden"])
              .fillna("")
        )

        # --- 7.9 Eliminar duplicados con datos llenos ---
        subset_dup_cols = [
            "CENTRO", "PERIODO", "DOC_PACIENTE", "PACIENTE", "EDAD", "TEL_MOVIL",
            "SERVICIO_match", "ACTIVIDAD", "SUBACTIVIDAD", "MES_match",
            "FECHA_ATENCION", "DNI_MEDICO_match", "PROFESIONAL_match"
        ]
        mask_no_blank = df_res[subset_dup_cols].replace('', pd.NA).notna().all(axis=1)
        dup_mask = df_res.duplicated(subset=subset_dup_cols, keep='first') & mask_no_blank
        df_res = df_res[~dup_mask].reset_index(drop=True)

        # --- 7.10 NUEVO: crear columna unificada DOCUMENTO_PACIENTE ---
        df_res["DOCUMENTO_PACIENTE"] = df_res["DOC_PACIENTE"].where(
            df_res["DOC_PACIENTE"] != "", df_res["DOC_PACIENTE_citas"]
        )

        # --- 7.11 Orden de columnas final (unificada primero) ---
        cols_final = [
            "DOCUMENTO_PACIENTE",    
            "PACIENTE",
            "CENTRO", "PERIODO",
             "EDAD", "TEL_MOVIL", 
            "SERVICIO_match", "ACTIVIDAD", "SUBACTIVIDAD",
            "MES_match", "FECHA_ATENCION",
            "FECHA_SOLIC_match", "FECHA_CITA_match",
            "DNI_MEDICO_match", "PROFESIONAL_match",
            "TURNO",
            "SERVICIO_citas",
            "FECHA_SOLIC_citas", "MES_citas", "FECHA_CITA_citas",
            "ESTADO_CITA", "TIPO_CITA", "H_C", "DNI_MEDICO_citas",
            "PROFESIONAL CITA", "OBSERVACION"
        ]
        df_res = df_res.reindex(columns=cols_final)

        # --- 7.12 Filtrar DOCUMENTO_PACIENTE presente en ambos datasets ---
        docs_explota = set(df_total_explota["DOC_PACIENTE"].unique())
        docs_citas   = set(df_citas["DOC_PACIENTE"].unique())
        docs_intersect = docs_explota & docs_citas
        df_res = df_res[df_res["DOCUMENTO_PACIENTE"].isin(docs_intersect)]

        # --- 7.13 Descargas + previsualización ---
        st.success("Resultado final listo ✅")

        col_txt, col_xlsx = st.columns(2)
        with col_txt:
            txt_final = df_res.to_csv(
                sep="|", index=False, lineterminator="\n"
            ).encode("utf-8")
            st.download_button(
                "⬇️ Haz click para bajar TXT",
                txt_final,
                file_name=nombre_archivo("resultado_final", "txt"),
                mime="text/plain",
                key="final_txt_dl"
            )
        with col_xlsx:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                df_res.to_excel(writer, index=False, sheet_name="ResultadoFinal")
            st.download_button(
                "⬇️ Haz click para bajar Excel",
                buf.getvalue(),
                file_name=nombre_archivo("resultado_final", "xlsx"),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="final_xlsx_dl"
            )

        # Previsualización
        st.write(f"Total filas: {len(df_res)}")
        st.dataframe(df_res.reset_index(drop=True))

else:
    st.info("Carga Explota Match y Citas Médicas para generar el resultado final.")