"""Etapa 3: variables analíticas seleccionadas; sin normalización ni IOT."""
from pathlib import Path
import pandas as pd, numpy as np, json
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]; E=next((R/'episodios').glob('002_EL_*')); D=E/'Data'; O=D/'processed'; N=E/'notebooks'; F=E/'outputs'/'etapa_3'; N.mkdir(exist_ok=True); F.mkdir(parents=True,exist_ok=True)
V=['cobertura_movil_3g_4g_pct','penetracion_internet_fijo_2025_t3_pct','ipm_censo_2018','porcentaje_poblacion_rural','indice_brecha_conectividad_fisica','ips_por_10000_hab','sgp_per_capita_2027']
def main():
 a=pd.read_csv(O/'dataset_analitico_preliminar_iot.csv',dtype={'divipola':'string'}); a.divipola=a.divipola.str.zfill(5); sgp=pd.read_csv(next(O.glob('dataset_09*.csv')),dtype={'divipola':'string'}); sgp.divipola=sgp.divipola.str.zfill(5)
 a=a.merge(sgp[['divipola','municipio_fuente','poblacion_proyectada_2027']],on='divipola',how='left')
 # IPS comes from Dataset 08 in preliminary analytic table; 2027 population is explicit denominator.
 a['ips_por_10000_hab']=a.ips_total/a.poblacion_proyectada_2027*10000; a['sgp_per_capita_2027']=a.sgp_total_asignado_2027/a.poblacion_proyectada_2027
 out=a[['divipola','municipio']].copy(); out['municipio_homologado']=out.municipio; out['municipio_fuente']=a.get('municipio_fuente',out.municipio)
 for v in V: out[v]=a[v]
 out.to_csv(O/'dataset_analitico_etapa_3_iot.csv',index=False)
 ctx=out[['divipola','municipio','municipio_homologado','municipio_fuente']].copy(); ctx['distancia_quibdo_km']=a.distancia_quibdo_km; ctx['medios_locales_total']=a.medios_locales_total; ctx.to_csv(O/'dataset_contextual_etapa_3_iot.csv',index=False)
 meta=[]
 info={'cobertura_movil_3g_4g_pct':('Acceso digital','2025? fuente base 2018','porcentaje','+','Cobertura de red móvil 3G/4G','uso efectivo'),'penetracion_internet_fijo_2025_t3_pct':('Acceso digital','2025-T3','porcentaje','+','Penetración de internet fijo','uso efectivo'),'ipm_censo_2018':('Condiciones socioeconómicas','2018','índice/porcentaje según fuente','-','Privación multidimensional','causalidad'),'porcentaje_poblacion_rural':('Ruralidad','2018','porcentaje','-','Proporción de población rural','menor oportunidad automática'),'indice_brecha_conectividad_fisica':('Conectividad física','según Dataset 03','índice','- según definición de brecha','Brecha física','causalidad'),'ips_por_10000_hab':('Salud / presencia institucional','REPS 2026; población 2027','sedes por 10.000 hab','+','Densidad de sedes IPS registradas','calidad/cobertura efectiva'),'sgp_per_capita_2027':('Recursos públicos','2027','COP corrientes por habitante','+','SGP asignado/proyectado por habitante','ejecución/resultados')}
 for v in V:
  x=info[v]; meta.append(dict(variable=v,nombre_legible=v.replace('_',' '),dimension=x[0],fuente='Datasets procesados 01/02/03/05/08/09',periodo=x[1],unidad=x[2],denominador='poblacion_proyectada_2027' if v in ['ips_por_10000_hab','sgp_per_capita_2027'] else 'no aplica',direccion=x[3],que_mide=x[4],que_no_mide=x[5],transformacion_aplicada='ips_total/poblacion_proyectada_2027*10000' if v=='ips_por_10000_hab' else 'sgp_total_asignado_2027/poblacion_proyectada_2027' if v=='sgp_per_capita_2027' else 'ninguna',transformacion_pendiente='normalización en etapa siguiente',limitaciones='sin imputación; revisar temporalidad'))
 pd.DataFrame(meta).to_csv(O/'metadatos_variables_etapa_3_iot.csv',index=False)
 rows=[]
 for v in V:
  s=out[v]; q=s.quantile([.25,.5,.75]); rows.append(dict(variable=v,n_municipios=s.notna().sum(),cobertura_pct=round(s.notna().mean()*100,2),nulos=s.isna().sum(),ceros=(s==0).sum(),minimo=s.min(),maximo=s.max(),media=s.mean(),mediana=q.loc[.5],desviacion_estandar=s.std(),p25=q.loc[.25],p75=q.loc[.75],iqr=q.loc[.75]-q.loc[.25],coeficiente_variacion=s.std()/s.mean() if s.mean()!=0 else np.nan,asimetria=s.skew(),outliers_iqr=((s<q.loc[.25]-1.5*(q.loc[.75]-q.loc[.25]))|(s>q.loc[.75]+1.5*(q.loc[.75]-q.loc[.25]))).sum()))
 S=pd.DataFrame(rows); S.to_csv(O/'estadisticas_variables_etapa_3_iot.csv',index=False); S[['variable','n_municipios','cobertura_pct','nulos','ceros']].to_csv(O/'cobertura_variables_etapa_3_iot.csv',index=False)
 cor=[]
 for m in ['pearson','spearman']:
  c=out[V].corr(method=m)
  for i,x in enumerate(V):
   for y in V[i+1:]: cor.append(dict(metodo=m,variable_a=x,variable_b=y,coeficiente=c.loc[x,y]))
 pd.DataFrame(cor).to_csv(O/'correlaciones_variables_etapa_3_iot.csv',index=False)
 pd.DataFrame([dict(variable=x,periodo=info[x][1],fuente='ver metadatos',poblacion_periodo='2027 sólo para IPS y SGP',compatibilidad_temporal='parcial',observacion='sin ajuste temporal') for x in V]).to_csv(O/'comparabilidad_temporal_etapa_3_iot.csv',index=False)
 pd.DataFrame([{'hallazgo':'Dataset 04 no recuperable; notebook indica construcción histórica pero no hay artefacto.','decision':'No incorporación independiente; función potencialmente cubierta por variables existentes.'},{'hallazgo':'Variables originales preservadas.','decision':'No imputación, normalización, pesos, score ni ranking.'}]).to_csv(O/'auditoria_etapa_3_iot.csv',index=False)
 pd.DataFrame([{'decision':'Conjunto de siete variables construido según selección humana.','estado':'implementado'},{'decision':'Direcciones conceptuales documentadas; no invertidas matemáticamente.','estado':'pendiente etapa normalización'}]).to_csv(O/'decisiones_metodologicas_etapa_3_iot.csv',index=False)
 fig,ax=plt.subplots(figsize=(11,6)); out[V].boxplot(ax=ax,rot=60); ax.set_title('Etapa 3: distribuciones en escalas originales'); fig.tight_layout(); fig.savefig(F/'boxplots_variables_analiticas.png',dpi=150); plt.close(fig)
 nb={'cells':[{'cell_type':'markdown','metadata':{},'source':['# Etapa 3\n','Construcción reproducible; sin índice.']},{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':["from pathlib import Path\nimport runpy\nr=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'scripts'/'construir_variables_etapa_3_iot.py').exists())\nrunpy.run_path(str(r/'scripts'/'construir_variables_etapa_3_iot.py'),run_name='__main__')"]}], 'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},'nbformat':4,'nbformat_minor':5}; (N/'013_variables_analiticas_etapa_3_iot.ipynb').write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
if __name__=='__main__': main()
