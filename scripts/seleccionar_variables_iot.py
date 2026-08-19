"""Etapa 2: inventario, EDA y selección preliminar sin construir un IOT."""
from pathlib import Path
from datetime import date
import json, logging, re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]; EP=next((ROOT/'episodios').glob('002_EL_*')); DATA=EP/'Data'; RAW=DATA/'raw'; OUT=DATA/'processed'; LOG=EP/'logs'; NB=EP/'notebooks'; FIG=EP/'outputs'/'etapa_2'
OUT.mkdir(exist_ok=True); LOG.mkdir(exist_ok=True); NB.mkdir(exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
logging.basicConfig(filename=LOG/'seleccion_variables_iot.log',encoding='utf-8',level=logging.INFO,format='%(asctime)s | %(message)s')

def one(folder,pat):
    x=list(folder.glob(pat)); return x[0] if x else None
def csv(p): return pd.read_csv(p,dtype={'divipola':'string'})
def normid(d):
    if 'divipola' in d: d['divipola']=d.divipola.astype('string').str.replace(r'\.0$','',regex=True).str.zfill(5)
    return d
def load():
    spec=[('01',one(RAW,'dataset_01_poblacion_territorio_choco_definitivo.csv'),None),('02',one(RAW,'dataset_02_*.csv'),None),('03',one(OUT,'dataset_03*.csv') or one(RAW,'dataset_03*.csv'),None),('05',one(RAW,'dataset_05*.csv'),None),('06',one(RAW,'dataset_06*.xlsx'),'Base_municipal'),('07',one(RAW,'dataset_07*.xlsx'),'Municipio_anio'),('08',one(OUT,'dataset_08*.csv') or one(RAW,'dataset_08*.xlsx'),'Municipio'),('09',one(OUT,'dataset_09*.csv'),None),('10',one(OUT,'dataset_10*.csv'),None)]
    ans={}
    for ds,p,sh in spec:
        if not p: logging.info('Dataset %s no disponible',ds); continue
        d=csv(p) if p.suffix=='.csv' else pd.read_excel(p,sheet_name=sh)
        ans[ds]=normid(d); logging.info('Dataset %s %s %s',ds,p.name,d.shape)
    return ans
def dimension(col,ds):
    c=col.lower()
    if any(x in c for x in ['internet','movil','acceso','fibra','operador','digital']): return 'acceso_digital'
    if any(x in c for x in ['brecha','carretero','fluvial','movilidad','distancia']): return 'conectividad_fisica_territorio'
    if any(x in c for x in ['ipm','nbi','deficit','pobreza','hacinamiento','vivienda']): return 'condiciones_socioeconomicas'
    if any(x in c for x in ['policia','ejercito','ips','urgencias','institucional']): return 'capacidad_institucional_servicios'
    if any(x in c for x in ['sgp','inversion','asignado']): return 'recursos_publicos'
    if any(x in c for x in ['poblacion','rural','densidad','superficie','centros']): return 'territorio_demografia'
    if any(x in c for x in ['medio','emisora','prensa','informacion']): return 'ecosistema_informativo'
    return 'sin_dimension_clara'
def direction(c):
    x=c.lower()
    if any(z in x for z in ['ipm','nbi','deficit','brecha','distancia','hacinamiento']): return 'alto=menor_oportunidad (provisional)'
    if any(z in x for z in ['cobertura','penetracion','acceso','ips','urgencias','medio']): return 'alto=mayor_oportunidad (provisional)'
    return 'no_determinada'
def main():
    D=load(); u=D['01'][['divipola','municipio']].copy(); inv=[]; stats=[]; selected=[]
    # Selection is deliberately conservative: established coverage/rate indicators and deprivation measures.
    strong={'02':['penetracion_internet_fijo_2025_t3_pct','cobertura_movil_3g_4g_pct'],'05':['ipm_censo_2018','nbi_2018'],'06':['medios_locales_total'],'08':['ips_total']}
    transform={'01':['porcentaje_poblacion_rural','indice_ruralidad_existente','distancia_quibdo_km'],'03':['indice_brecha_conectividad_fisica'],'09':['sgp_total_asignado_2027']}
    analytic=u.copy()
    for ds,d in D.items():
        for c in d.columns:
            if c in ['divipola','municipio','departamento','municipio_homologado','municipio_fuente'] : continue
            numeric=pd.api.types.is_numeric_dtype(d[c]) and not pd.api.types.is_bool_dtype(d[c]); n=int(d[c].notna().sum()); uniq=int(d[c].nunique(dropna=True)); cov=round(n/len(d)*100,2)
            status='E_contextual' if ds=='10' or not numeric else 'C_limitaciones'
            if c in strong.get(ds,[]): status='A_candidata_fuerte'
            if c in transform.get(ds,[]): status='B_requiere_transformacion'
            if c.startswith('poblacion_') or c in ['anio','alerta_sgp_2027']: status='D_descartada'
            inv.append(dict(dataset=ds,nombre_original=c,nombre_procesado=c,definicion='Ver documentación del dataset de origen',unidad='no especificada en tabla consolidada',tipo_variable='numerica' if numeric else 'categorica/texto',unidad_territorial='municipio' if 'divipola' in d else 'no municipal',periodo='segun dataset',cobertura_pct=cov,nulos=len(d)-n,valores_unicos=uniq,fuente=f'Dataset {ds}',dimension_potencial=dimension(c,ds),observaciones_metodologicas='Revisión preliminar; no implica inclusión.'))
            if numeric:
                s=pd.to_numeric(d[c],errors='coerce').dropna(); q=s.quantile([.25,.5,.75]).to_dict(); cv=float(s.std()/s.mean()) if s.mean()!=0 else np.nan
                stats.append(dict(dataset=ds,variable=c,n=n,nulos=len(d)-n,minimo=s.min() if n else np.nan,maximo=s.max() if n else np.nan,media=s.mean() if n else np.nan,mediana=q.get(.5),desv_est=s.std() if n else np.nan,p25=q.get(.25),p75=q.get(.75),coef_variacion=cv,asimetria=s.skew() if n>2 else np.nan,ceros=int((s==0).sum()),valores_unicos=uniq,casi_constante=bool(uniq<=2 or (n and (s==0).mean()>=.8))))
            reason=('Definición/cobertura comparables; pendiente validación humana.' if status.startswith('A') else 'Requiere ajuste de escala o denominador antes de comparación.' if status.startswith('B') else 'No se recomienda para IOT en esta etapa.' if status.startswith('D') else 'Evidencia contextual o limitación de cobertura/periodo.')
            selected.append(dict(dataset=ds,variable=c,clasificacion=status,dimension=dimension(c,ds),pertinencia='alta' if status.startswith('A') else 'media' if status.startswith('B') else 'no clara',comparabilidad='si' if status.startswith('A') else 'parcialmente',direccion=direction(c),transformacion_propuesta='ninguna' if status.startswith('A') else 'per_capita/tasa o revisión metodológica' if status.startswith('B') else 'ninguna',motivo=reason))
        keep=[c for c in strong.get(ds,[])+transform.get(ds,[]) if c in d and 'divipola' in d]
        if keep: analytic=analytic.merge(d[['divipola']+keep],on='divipola',how='left',validate='one_to_one')
    INV=pd.DataFrame(inv); STA=pd.DataFrame(stats); SEL=pd.DataFrame(selected)
    INV.to_csv(OUT/'inventario_variables_iot.csv',index=False); STA.to_csv(OUT/'estadisticas_variables_iot.csv',index=False); SEL.to_csv(OUT/'seleccion_variables_iot.csv',index=False)
    analytic.to_csv(OUT/'dataset_analitico_preliminar_iot.csv',index=False)
    cov=pd.DataFrame([{'variable':c,'nulos':int(analytic[c].isna().sum()),'cobertura_pct':round(analytic[c].notna().mean()*100,2)} for c in analytic.columns if c not in ['divipola','municipio']]); cov.to_csv(OUT/'cobertura_variables_iot.csv',index=False)
    num=analytic.drop(columns=['divipola','municipio']).select_dtypes('number'); corr=num.corr(); rows=[]
    for i,a in enumerate(corr.columns):
        for b in corr.columns[i+1:]: rows.append({'variable_a':a,'variable_b':b,'correlacion_pearson':corr.loc[a,b],'tipo':'estadistica' if abs(corr.loc[a,b])>=.7 else 'sin_alerta_estadistica'})
    pd.DataFrame(rows).to_csv(OUT/'redundancias_variables_iot.csv',index=False)
    pd.DataFrame([{'pregunta':'¿Qué variables cambian al ajustar recursos o servicios por población?','tipo':'descriptiva_no_causal'},{'pregunta':'¿Qué dimensiones muestran mayor heterogeneidad municipal?','tipo':'descriptiva_no_causal'},{'pregunta':'¿Qué indicadores comparten patrones estadísticos sin implicar causalidad?','tipo':'descriptiva_no_causal'}]).to_csv(OUT/'preguntas_analisis_iot.csv',index=False)
    pd.DataFrame([{'hallazgo':'Dataset 04 no está disponible en RAW ni PROCESSED.','impacto':'Dimensión potencial no evaluada.'},{'hallazgo':'Datasets 07 y 09 tienen temporalidad o unidad no directamente comparable.','impacto':'No se incluyen automáticamente como candidatas fuertes.'},{'hallazgo':'Dataset 10 es contextual y no municipal.','impacto':'Excluido del dataset analítico.'}]).to_csv(OUT/'auditoria_seleccion_variables_iot.csv',index=False)
    if len(num.columns):
        fig,ax=plt.subplots(figsize=(10,6)); num.boxplot(ax=ax,rot=60); ax.set_title('Análisis descriptivo preliminar: variables candidatas'); ax.set_ylabel('Escalas originales (no comparables)'); fig.tight_layout(); fig.savefig(FIG/'distribuciones_preliminares.png',dpi=150); plt.close(fig)
    nb={'cells':[{'cell_type':'markdown','metadata':{},'source':['# Etapa 2 — análisis y selección metodológica\n','Cuaderno ejecutable: no construye un score IOT.']},{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':["from pathlib import Path\nimport runpy\nroot=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'scripts'/'seleccionar_variables_iot.py').exists())\nrunpy.run_path(str(root/'scripts'/'seleccionar_variables_iot.py'),run_name='__main__')"]}] ,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},'nbformat':4,'nbformat_minor':5}
    (NB/'011_analisis_seleccion_variables_iot.ipynb').write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
    logging.info('Etapa 2 terminada: %s variables, analítico %s',len(INV),analytic.shape)
if __name__=='__main__': main()
