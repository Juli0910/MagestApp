import streamlit as st
import pandas as pd
import io, xlsxwriter
from datetime import datetime
import pytz

# --------------------------------------------------
# Configuración de la pestaña
# --------------------------------------------------
st.set_page_config(page_title="Magest App", page_icon="🩺")
st.title("🤰 Magest App")
st.markdown("---")

# --------------------------------------------------
# Diccionario de CENTRO (código → nombre completo)
# --------------------------------------------------
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

# --------------------------------------------------
# Columnas de origen
# --------------------------------------------------
columnas_explota = [
    "CENTRO", "PERIODO", "SERVICIO", "ACTIVIDAD", "SUBACTIVIDAD",
    "PROFESIONAL", "FECHA_ATENCION", "DOC_PACIENTE", "PACIENTE", "ANNOS",
    "FECHA_SOLIC", "FECHA_CITA", "DES_DIAGNOSTICO", "TIPODIAG", "TIPO_GRAVIDEZ"
]

columnas_citas = [
    "CENTRO", "PERIODO", "SERVICIO", "CODACTIVIDAD", "ACTIVIDAD", "SUBACTIVIDAD",
    "FECHA_SOLIC", "FECHA_CITA", "ESTADO_CITA", "TIPO_CITA", "H_C", "DNI_MEDICO",
    "PROFESIONAL", "DOC_PACIENTE", "PACIENTE", "EDAD", "TEL_MOVIL", "TURNO",
    "TIP_PROGRAMACION"
]

# --------------------------------------------------
# Columnas a mostrar en cada sección
# --------------------------------------------------
cols_show_explota = [
    "CENTRO", "PERIODO", "DOC_PACIENTE", "PACIENTE", "SERVICIO",
    "ACTIVIDAD", "SUBACTIVIDAD", "PROFESIONAL", "FECHA_ATENCION", "ANNOS",
    "FECHA_SOLIC", "FECHA_CITA", "DES_DIAGNOSTICO", "TIPODIAG", "TIPO_GRAVIDEZ"
]

cols_show_citas = [
    "CENTRO", "PERIODO", "DOC_PACIENTE", "PACIENTE", "SERVICIO",
    "CODACTIVIDAD", "ACTIVIDAD", "SUBACTIVIDAD", "FECHA_SOLIC", "FECHA_CITA",
    "ESTADO_CITA", "TIPO_CITA", "H_C", "DNI_MEDICO", "PROFESIONAL",
    "EDAD", "TEL_MOVIL", "TURNO", "TIP_PROGRAMACION"
]

# --------------------------------------------------
# Cabeceras finales
# --------------------------------------------------
cabeceras_finales = [
    "CENTRO", "PERIODO", "DOC_PACIENTE", "PACIENTE", "SERVICIO",
    "CODACTIVIDAD", "ACTIVIDAD", "SUBACTIVIDAD", "FECHA_SOLIC", "MES",
    "FECHA_CITA", "ESTADO_CITA", "TIPO_CITA", "H_C", "DNI_MEDICO",
    "PROFESIONAL", "EDAD", "TEL_MOVIL", "TURNO", "TIP_PROGRAMACION"
]
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
    "Y": "HOSPITAL I AURELIO DIAZ UFANO Y PERAL",
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

# --------------------------------------------------
# Mapeos y utilidades
# --------------------------------------------------
nombres_equivalentes = {
    "APENOMB_MEDICO": "PROFESIONAL",
    "DESC_DIAGNOSTICO": "DES_DIAGNOSTICO",
    "TIPO_DIAG": "TIPODIAG",
    "DNI": "DOC_PACIENTE"
}

meses_es = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def mes_es(fecha_str: str) -> str:
    fecha = pd.to_datetime(fecha_str, dayfirst=True, errors="coerce")
    if pd.isna(fecha):
        fecha = pd.to_datetime(fecha_str, errors="coerce")
    return meses_es.get(fecha.month, "") if not pd.isna(fecha) else ""

def non_empty_count(row: pd.Series) -> int:
    return row.replace("", pd.NA).notna().sum()

def nombre_archivo(seccion: str, extension: str) -> str:
    lima = pytz.timezone("America/Lima")
    ahora = datetime.now(lima)
    return f"{seccion}_{ahora.strftime('%Y%m%d_%H%M')}.{extension}"

def aplicar_centro_map_contains(texto):
    for palabra, nombre_completo in CENTRO_MAP_RESULT_FINAL.items():
        if pd.notna(texto) and palabra.upper() in texto.upper():
            return nombre_completo
    return texto
# --------------------------------------------------
# Estado UI
# --------------------------------------------------
st.session_state.setdefault("show_explota", False)
st.session_state.setdefault("show_citas",   False)
st.session_state.setdefault("generate_pressed", False)

# ==================================================
# 1. EXPLOTA MATCH (solo GESTANTE)
# ==================================================
st.header("📂 Explota Match")

explota_files = st.file_uploader(
    "Sube uno o más archivos .txt para Explota Match",
    type=["txt"], accept_multiple_files=True, key="explota"
)

df_total_explota = pd.DataFrame()
errores_explota = []

if explota_files:
    dfs_validos = []
    for f in explota_files:
        try:
            df = pd.read_csv(f, sep="|", dtype=str)
            df.columns = df.columns.str.strip()
            df.rename(columns=nombres_equivalentes, inplace=True)

            if "TIPODIAG" in df.columns:
                df["TIPODIAG"] = df["TIPODIAG"].replace({"P": "PRESUNTIVO", "D": "DEFINITIVO"})

            faltan = [c for c in columnas_explota if c not in df.columns]
            if faltan:
                errores_explota.append(f"{f.name}: faltan {', '.join(faltan)}")
            else:
                # Mapear CENTRO
                if "CENTRO" in df.columns:
                    df["CENTRO"] = df["CENTRO"].map(CENTRO_MAP).fillna(df["CENTRO"])
                dfs_validos.append(df)
        except Exception as e:
            errores_explota.append(f"Error en {f.name}: {e}")

    if errores_explota:
        st.warning("Problemas:")
        for err in errores_explota:
            st.markdown(f"- {err}")

    if dfs_validos:
        st.success("Explota cargado ✅")
        df_total_explota = pd.concat(dfs_validos, ignore_index=True)
        df_total_explota = df_total_explota[
            df_total_explota["TIPO_GRAVIDEZ"].fillna("").str.upper() == "GESTANTE"
        ].reset_index(drop=True)              # ← índice consecutivo

        if st.button("👁️ Ver/Ocultar Explota", key="tgl_explota"):
            st.session_state.show_explota = not st.session_state.show_explota
        if st.session_state.show_explota:
            st.write(f"Total filas: {len(df_total_explota)}")
            st.dataframe(df_total_explota[cols_show_explota])

# ==================================================
# 2. CITAS MÉDICAS
# ==================================================
st.markdown("---")
st.header("📋 Citas Médicas")

citas_file = st.file_uploader(
    "Sube un archivo .txt para Citas Médicas",
    type=["txt"], accept_multiple_files=False, key="citas"
)

df_citas = pd.DataFrame()
if citas_file:
    try:
        df_citas = pd.read_csv(citas_file, sep="|", dtype=str)
        df_citas.columns = df_citas.columns.str.strip()
        df_citas.rename(columns=nombres_equivalentes, inplace=True)

        faltan = [c for c in columnas_citas if c not in df_citas.columns]
        if faltan:
            st.warning(f"{citas_file.name}: faltan {', '.join(faltan)}")
        else:
            st.success("Citas cargado ✅")
            if st.button("👁️ Ver/Ocultar Citas", key="tgl_citas"):
                st.session_state.show_citas = not st.session_state.show_citas
            if st.session_state.show_citas:
                st.write(f"Total filas: {len(df_citas)}")
                st.dataframe(df_citas[cols_show_citas].reset_index(drop=True))
    except Exception as e:
        st.error(f"Error en {citas_file.name}: {e}")

# ==================================================
# 3. RESULTADO FINAL
# ==================================================
st.markdown("---")
st.header("📊 Resultado final")

if not df_total_explota.empty and not df_citas.empty:
    if st.button("⚙️ Generar resultado final", key="btn_generar"):
        st.session_state.generate_pressed = True

        with st.spinner("Generando..."):
            # --- intersección por DOC_PACIENTE ---
            docs_inter = set(df_total_explota["DOC_PACIENTE"].dropna()) & \
                         set(df_citas["DOC_PACIENTE"].dropna())

            df_expl = df_total_explota[df_total_explota["DOC_PACIENTE"].isin(docs_inter)]
            df_cit  = df_citas[df_citas["DOC_PACIENTE"].isin(docs_inter)]

            # --- formatear columnas homogéneas (Explota vs Citas) ---
            expl_cols_base = [
                "CENTRO","PERIODO","SERVICIO","ACTIVIDAD","SUBACTIVIDAD",
                "FECHA_SOLIC","FECHA_CITA","DOC_PACIENTE","PACIENTE","PROFESIONAL"
            ]
            cit_cols_extra = [
                "CODACTIVIDAD","ESTADO_CITA","TIPO_CITA","H_C","DNI_MEDICO",
                "EDAD","TEL_MOVIL","TURNO","TIP_PROGRAMACION"
            ]

            df_expl_fmt = df_expl[expl_cols_base].copy()
            for c in cit_cols_extra:
                df_expl_fmt[c] = ""

            df_cit_fmt = df_cit[expl_cols_base + cit_cols_extra].copy()

            df_union = pd.concat([df_expl_fmt, df_cit_fmt], ignore_index=True).drop_duplicates(
                subset=["DOC_PACIENTE","PACIENTE","FECHA_CITA","SERVICIO","CODACTIVIDAD"]
            )

            # --- pac-fecha con OBSTETRA y MEDICINA GENERAL ---
            req = {"OBSTETRA","MEDICINA GENERAL"}
            claves_ok = (
                df_union.groupby(["DOC_PACIENTE","PACIENTE","FECHA_CITA"])["SERVICIO"]
                .apply(lambda s: set(s.str.upper()))
                .reset_index()
            )
            claves_ok = claves_ok[claves_ok["SERVICIO"].apply(lambda s: req.issubset(s))]

            df_res = df_union.merge(claves_ok[["DOC_PACIENTE","PACIENTE","FECHA_CITA"]],
                                    on=["DOC_PACIENTE","PACIENTE","FECHA_CITA"],
                                    how="inner")

            # --- MES ---
            df_res["MES"] = df_res["FECHA_CITA"].apply(mes_es)

            # --- quitar duplicados manteniendo fila con más info ---
            df_res["_info"] = df_res.apply(non_empty_count, axis=1)
            df_res = (
                df_res.sort_values(
                    by=["DOC_PACIENTE","PACIENTE","FECHA_CITA","SERVICIO","_info"],
                    ascending=[True, True, True, True, False]
                )
                .drop_duplicates(subset=["DOC_PACIENTE","PACIENTE","FECHA_CITA","SERVICIO"], keep="first")
                .drop(columns="_info")
            )

            # --- seleccionar columnas finales y ordenar ---
            df_res = df_res.reindex(columns=cabeceras_finales).sort_values(
                ["DOC_PACIENTE","FECHA_CITA","SERVICIO"]
            ).reset_index(drop=True)
            df_res["CENTRO"] = df_res["CENTRO"].apply(aplicar_centro_map_contains)
            st.session_state.df_result = df_res

    # -------- mostrar y descargar --------
    if st.session_state.generate_pressed and "df_result" in st.session_state:
        st.success("Resultado final listo ✅")
        st.write(f"Total filas: {len(st.session_state.df_result)}")
        st.dataframe(st.session_state.df_result)

        col_txt, col_xlsx = st.columns(2)

        with col_txt:
            txt_data = st.session_state.df_result.to_csv(sep="|", index=False, lineterminator="\n")
            st.download_button("📥 Descargar TXT",
                               txt_data.encode("utf-8"),
                               file_name=nombre_archivo("resultado_final", "txt"),
                               mime="text/plain")

        with col_xlsx:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                st.session_state.df_result.to_excel(writer, index=False, sheet_name="ResultadoFinal")
            st.download_button("📥 Descargar Excel",
                               buf.getvalue(),
                               file_name=nombre_archivo("resultado_final", "xlsx"),
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("Carga Explota Match (GESTANTE) y Citas Médicas para generar el resultado final.")
