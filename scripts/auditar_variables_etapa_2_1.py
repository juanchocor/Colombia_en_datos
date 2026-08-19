"""Auditoría metodológica de candidatas IOT; no crea índice ni rankings."""
from pathlib import Path
from datetime import date
import json
import pandas as pd, numpy as np
import matplotlib.pyplot as plt

R=Path(__file__).resolve().parents[1]; E=next((R/'episodios').glob('002_EL_*')); D=E/'Data'; O=D/'processed'; N=E/'notebooks'; F=E/'outputs'/'etapa_2_1'; N.mkdir(exist_ok=True); F.mkdir(parents=True,exist_ok=True)
vars=['cobertura_movil_3g_4g_pct','penetracion_internet_fijo_2025_t3_pct','ipm_censo_2018','nbi_2018','medios_locales_total','ips_total','porcentaje_poblacion_rural','indice_ruralidad_existente','distancia_quibdo_km','indice_brecha_conectividad_fisica','sgp_total_asignado_2027']
meta={
'cobertura_movil_3g_4g_pct':('02','Acceso digital','porcentaje de cobertura móvil 3G/4G','porcentaje','2018','A','A'),
'penetracion_internet_fijo_2025_t3_pct':('02','Acceso digital','penetración de internet fijo','porcentaje','2025-T3','A','A'),
'ipm_censo_2018':('05','Condiciones socioeconómicas','índice de pobreza multidimensional censal','índice/porcentaje según fuente','2018','B','A'),
'nbi_2018':('05','Condiciones socioeconómicas','necesidades básicas insatisfechas','porcentaje según fuente','2018','B','A'),
'medios_locales_total':('06','Ecosistema informativo','conteo de medios locales registrados','conteo','según fuente','C','C'),
'ips_total':('08','Salud / servicios','conteo de sedes IPS registradas','conteo de sedes, no capacidad efectiva','corte REPS 2026','D','B'),
'porcentaje_poblacion_rural':('01','Conectividad física y territorio','proporción de población rural','porcentaje','2018','C','B'),
'indice_ruralidad_existente':('01','Conectividad física y territorio','índice de ruralidad existente','índice; requiere revisión','2018','C','B'),
'distancia_quibdo_km':('01','Conectividad física y territorio','distancia a Quibdó','kilómetros; requiere revisión','2018','C','D'),
'indice_brecha_conectividad_fisica':('03','Conectividad física y territorio','índice de brecha de conectividad física','índice; revisar construcción','según fuente','B','B'),
'sgp_total_asignado_2027':('09','Recursos públicos','asignación/proyección SGP total','pesos corrientes COP','2027','C','B')}
def main():
 a=pd.read_csv(O/'dataset_analitico_preliminar_iot.csv',dtype={'divipola':'string'}); pop=pd.read_csv(D/'raw'/'dataset_01_poblacion_territorio_choco_definitivo.csv',dtype={'divipola':'string'}); pop.divipola=pop.divipola.str.zfill(5); a=a.merge(pop[['divipola','poblacion_total']],on='divipola',how='left')
 # Exploratory denominators only; originals remain untouched.
 for v,name,scale in [('ips_total','ips_por_10000_hab',10000),('medios_locales_total','medios_por_10000_hab',10000),('sgp_total_asignado_2027','sgp_per_capita_2027',1)]: a[name]=a[v]/a.poblacion_total*scale
 audit=[]; stat=[]; temp=[]; trans=[]
 for v in vars:
  ds,dim,desc,unit,period,direc,cat=meta[v]; s=pd.to_numeric(a[v],errors='coerce'); n=s.notna().sum(); q=s.quantile([.25,.5,.75]); cv=s.std()/s.mean() if s.mean()!=0 else np.nan
  req='si' if cat=='B' else 'no'; proposal={'ips_total':'exploratoria: ips_por_10000_hab','medios_locales_total':'exploratoria: medios_por_10000_hab','sgp_total_asignado_2027':'exploratoria: sgp_per_capita_2027','porcentaje_poblacion_rural':'ninguna; revisar rol','indice_ruralidad_existente':'revisar redundancia con % rural','indice_brecha_conectividad_fisica':'revisar escala/dirección','distancia_quibdo_km':'sin dato; no transformable'}.get(v,'ninguna')
  limit='requiere revisión' if n==0 else ('cobertura parcial por Nuevo Belén de Bajirá' if n<31 else '')
  audit.append(dict(variable=v,dataset_origen=ds,dimension_propuesta=dim,unidad_de_observacion='municipio',tipo_de_variable='numerica',descripcion=desc,que_mide=desc,que_no_mide='oportunidad IOT directamente',unidad=unit,denominador_actual='no aplica / según fuente',denominador_recomendado='población para conteos y SGP; no aplica para porcentajes',año_periodo=period,cobertura_n=n,cobertura_pct=round(n/31*100,2),nulos=31-n,ceros=int((s==0).sum()),valores_unicos=s.nunique(),minimo=s.min(),maximo=s.max(),media=s.mean(),mediana=q.loc[.5],desviacion_estandar=s.std(),p25=q.loc[.25],p75=q.loc[.75],coeficiente_variacion=cv,direccion_conceptual=direc,requiere_transformacion=req,transformacion_propuesta=proposal,posibles_limitaciones=limit,posibles_redundancias='ver correlaciones',decision_provisional=f'{cat}: provisional'))
  stat.append(audit[-1]); temp.append(dict(variable=v,periodo=period,fuente=f'Dataset {ds}',comparabilidad_temporal='parcial',observacion='No se aplicaron ajustes temporales.'))
  if proposal.startswith('exploratoria'): trans.append(dict(variable_original=v,variable_derivada_propuesta=proposal.split(': ')[1],formula=f'{v} / poblacion_total' + (' * 10000' if v!='sgp_total_asignado_2027' else ''),estado='exploratoria; no sustituye original',riesgos='Población 2018 no es plenamente compatible con todos los cortes.'))
 A=pd.DataFrame(audit); A.to_csv(O/'auditoria_variables_etapa_2_1.csv',index=False); pd.DataFrame(stat).to_csv(O/'estadisticas_candidatas_etapa_2_1.csv',index=False); pd.DataFrame(temp).to_csv(O/'comparabilidad_temporal_etapa_2_1.csv',index=False); pd.DataFrame(trans).to_csv(O/'transformaciones_exploratorias_etapa_2_1.csv',index=False)
 pd.DataFrame([{'variable':v,'cobertura_n':int(a[v].notna().sum()),'cobertura_pct':round(a[v].notna().mean()*100,2),'nulos':int(a[v].isna().sum())} for v in vars]).to_csv(O/'cobertura_candidatas_etapa_2_1.csv',index=False)
 num=a[vars].apply(pd.to_numeric,errors='coerce'); rows=[]
 for method in ['pearson','spearman']:
  c=num.corr(method=method)
  for i,x in enumerate(vars):
   for y in vars[i+1:]: rows.append(dict(metodo=method,variable_a=x,variable_b=y,coeficiente=c.loc[x,y],alerta_alta=abs(c.loc[x,y])>.7 if pd.notna(c.loc[x,y]) else False,decision='revisar redundancia; no eliminar automáticamente'))
 pd.DataFrame(rows).to_csv(O/'correlaciones_candidatas_etapa_2_1.csv',index=False)
 dec=A[['variable','dimension_propuesta','direccion_conceptual','año_periodo','cobertura_pct','transformacion_propuesta','posibles_redundancias','posibles_limitaciones','decision_provisional']].rename(columns={'dimension_propuesta':'dimension','direccion_conceptual':'direccion','año_periodo':'periodo','posibles_redundancias':'redundancia','posibles_limitaciones':'problema_metodologico'}); dec['categoria_provisional']=dec.decision_provisional.str[0]; dec['requiere_revision_humana']=True; dec.to_csv(O/'decisiones_metodologicas_etapa_2_1.csv',index=False)
 pd.DataFrame([{'pregunta':'¿IPM y NBI son complementarios o sobrerrepresentan privación?','razon':'correlación y diferencia conceptual.'},{'pregunta':'¿Medios locales debe permanecer contextual?','razon':'cobertura cero en la tabla analítica.'},{'pregunta':'¿Qué produjo Dataset 04?','razon':'notebook lo referencia, pero no hay artefacto recuperable.'}]).to_csv(O/'preguntas_revision_humana_etapa_2_1.csv',index=False)
 fig,ax=plt.subplots(figsize=(10,6)); num.dropna(axis=1,how='all').boxplot(ax=ax,rot=65); ax.set_title('Auditoría exploratoria: escalas originales'); fig.tight_layout(); fig.savefig(F/'distribuciones_candidatas.png',dpi=150); plt.close(fig)
 nb={'cells':[{'cell_type':'markdown','metadata':{},'source':['# Etapa 2.1 — Auditoría metodológica\n','No genera índice, pesos ni ranking.']},{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':["from pathlib import Path\nimport runpy\nr=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'scripts'/'auditar_variables_etapa_2_1.py').exists())\nrunpy.run_path(str(r/'scripts'/'auditar_variables_etapa_2_1.py'),run_name='__main__')"]}], 'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},'nbformat':4,'nbformat_minor':5}; (N/'012_auditoria_metodologica_candidatas_iot.ipynb').write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
if __name__=='__main__': main()
