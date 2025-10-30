def dividir_dataframe_en_chunks(df, chunk_size):
  """
  Dividir el data-frame en chunks porque Excel no permite la division directa con Pandas.
  """
  for inicio in range(0, len(df), chunk_size):
    yield df.iloc[inicio:inicio + chunk_size]
