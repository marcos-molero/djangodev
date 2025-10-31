
CREATE OR REPLACE VIEW ilh001v0 AS
SELECT  
    TO_TIMESTAMP(
        LPAD(h001004::text, 4, '0') || '-' ||
        LPAD(h001005::text, 2, '0') || '-' ||
        LPAD(h001006::text, 2, '0') || ' ' ||
        LPAD(SUBSTRING(h001014::text FROM 1 FOR 2), 2, '0') || ':' ||
        LPAD(SUBSTRING(h001014::text FROM 3 FOR 2), 2, '0') || ':' ||
        LPAD(SUBSTRING(h001014::text FROM 5 FOR 2), 2, '0'),
        'YYYY-MM-DD HH24:MI:SS'
    ) AS fechahora,
    h001001, h001002, h001003, h001004, h001005, h001006,
    h001007, h001008, h001009, h001010, h001011, h001012,
    h001013, h001014, h001015, h001016, h001017, h001018,
    h001019, h001020, h001021, h001022, h001023, h001024,
    h001025, h001026, h001027, h001028, h001029, h001030
FROM ilh001 a;
   

CREATE OR REPLACE VIEW ilh002v0 (
    h002v001,
    h002v002,
    h002v003,
    h002v004,
    h002v005,
    h002v006,
    h002v007,
    h002v008
) AS
SELECT 
    h002001,
    h002002,
    h002003,
    h002004,
    h002006,
    SUM(h002007) AS h002v007,
    SUM(h002009) AS h002v008,
    SUM(h002015) AS h002v009
FROM ilh002
WHERE h002001 > 0
  AND h002003 <> ''
  AND h002004 <> ''
  AND h002009 <> 0
  AND h002013 = ' '
GROUP BY 
    h002001,
    h002002,
    h002003,
    h002004,
    h002006;
  
CREATE OR REPLACE VIEW ilh002v1 (
    h002v101,
    h002v102,
    h002v103,
    h002v104,
    h002v105,
    h002v106,
    h002v107,
    h002v108
) AS
SELECT 
    h002001,
    h002002,
    h002003,
    h002004,
    h002006,
    SUM(h002007) AS h002v106,
    SUM(h002009) AS h002v107,
    SUM(h002015) AS h002v108
FROM ilh002
WHERE h002001 > 0
  AND h002003 <> ''
  AND h002004 <> ''
  AND h002009 <> 0
  AND h002013 = 'F'
GROUP BY 
    h002001,
    h002002,
    h002003,
    h002004,
    h002006;
  
CREATE OR REPLACE VIEW ilh002v2 (
    h002v201,
    h002v202,
    h002v203,
    h002v204,
    h002v205,
    h002v206,
    h002v207,
    h002v208
) AS
SELECT 
    h002001,
    h002002,
    h002003,
    h002004,
    h002005,
    SUM(h002007) AS h002v206,
    SUM(h002009) AS h002v207,
    SUM(h002015) AS h002v208
FROM ilh002
WHERE h002001 > 0
  AND h002007 <> 0
  AND h002003 <> ''
  AND h002004 <> ''
  AND h002009 <> 0
  AND h002013 = ' '
GROUP BY 
    h002001,
    h002002,
    h002003,
    h002004,
    h002005;
  
CREATE OR REPLACE VIEW ilh002v3 (
    h002v301,
    h002v302,
    h002v303,
    h002v304,
    h002v305,
    h002v306,
    h002v307,
    h002v308
) AS
SELECT 
    h002001,
    h002002,
    h002003,
    h002004,
    h002005,
    SUM(h002007) AS h002v306,
    SUM(h002009) AS h002v307,
    SUM(h002015) AS h002v308
FROM ilh002
WHERE h002001 > 0
  AND h002009 <> 0
  AND h002003 <> ''
  AND h002004 <> ''
  AND h002013 = 'F'
GROUP BY 
    h002001,
    h002002,
    h002003,
    h002004,
    h002005;
  
CREATE OR REPLACE VIEW ilh002v4 (
    h002v401,
    h002v402,
    h002v403,
    h002v404,
    h002v405,
    h002v406,
    h002v407,
    h002v408
) AS
SELECT 
    h002001,
    h002002,
    h002003,
    h002004,
    EXTRACT(MONTH FROM h002005) AS h002v405,
    SUM(h002007) AS h002v406,
    SUM(h002009) AS h002v407,
    SUM(h002015) AS h002v408
FROM ilh002
WHERE h002001 > 0
  AND h002009 <> 0
  AND h002003 <> ''
  AND h002004 <> ''
GROUP BY 
    h002001,
    h002002,
    h002003,
    h002004,
    EXTRACT(MONTH FROM h002005);
  
CREATE OR REPLACE VIEW ilh002v9 (
    h002v901,
    h002v902,
    h002v903,
    h002v904,
    h002v905,
    h002v906,
    h002v907,
    h002v908
) AS
SELECT 
    h002001,
    h002002,
    h002003,
    h002004,
    CASE 
        WHEN h002006 < 7 THEN 'M'
        WHEN h002006 < 12 THEN 'A'
        WHEN h002006 < 19 THEN 'P'
        ELSE 'N'
    END AS h002v905,
    SUM(h002007) AS h002v906,
    SUM(h002009) AS h002v907,
    SUM(h002015) AS h002v908
FROM ilh002
WHERE h002001 > 0
  AND h002003 <> ''
  AND h002004 <> ''
  AND h002007 <> 0
  AND h002013 = ' '
GROUP BY 
    h002001,
    h002002,
    h002003,
    h002004,
    H002006;
  
CREATE OR REPLACE VIEW ilh003v0 AS
SELECT
  h003001,
  h003002,
  can.r001003 AS wh003002,
  h003003,
  COALESCE(mon.m002002, 'No Def.') AS wh003003,
  h003004 * 10000 + h003005 * 100 + h003006 AS wfecha,
  h003007,
  h003008,
  COALESCE(m004002, 'No Def.') AS wh003008,
  COALESCE(m004003, 'No Def.') AS cod_gra,
  COALESCE(gra.r001003, 'No Def.') AS wm004003,
  COALESCE(m004004, 'No Def.') AS cod_acc,
  COALESCE(acc.r001003, 'No Def.') AS wm004004,
  h003009,
  h003010,
  h003011,
  h003012,
  h003013,
  CASE h003013 WHEN 'D' THEN 'Debito' ELSE 'Credito' END AS wh003013,
  h003014,
  LPAD(h003015::text, 6, '0') AS hora_lk1,
  h003016,
  h003017,
  COALESCE(tip.r001003, 'No Def.') AS wh003017,
  h003018,
  h003019,
  h003020,
  h003021,
  COALESCE(h003022, ' ') AS h003022,
  COALESCE(ges.r001003, ' ') AS wh003022,
  COALESCE(h003023, 0) AS h003023,
  COALESCE(txn.r001003, 'No Def.') AS wh003023,
  COALESCE(h003024, ' ') AS h003024,
  COALESCE(h003025, 0) AS h003025,
  COALESCE(res.r001003, 'No Def.') AS wh003025,
  h003026,
  COALESCE(nod.r001003, 'No Def.') AS wh003026,
  h003027,
  COALESCE(h003028, ' ') AS h003028,
  COALESCE(ent.r001003, 'No Def.') AS wh003028,
  COALESCE(h003029, ' ') AS h003029,
  CASE h003029
    WHEN 'N' THEN 'Persona Natural'
    WHEN 'J' THEN 'Persona Juridica'
    WHEN 'G' THEN 'Gobierno'
    WHEN 'T' THEN 'Terminal'
    WHEN ' ' THEN 'No Def.'
    ELSE ' '
  END AS wh003029,
  TRIM(m004003) || TRIM(h003008) || h003032::text AS graaler,
  CASE h003030
    WHEN ' ' THEN 'ILOOK'
    ELSE h003030
  END AS h003030,
  h003031,
  COALESCE(h003033, 0) AS h003033,
  h003034,
  COALESCE(h003035, 0) AS h003035,
  h003036,
  h003037,
  h003038,
  COALESCE(rie.r001003, 'No Def.') AS wh003038,
  COALESCE(h003039, 0) AS h003039,
  COALESCE(tpr.r001003, 'No Def.') AS wh003039,
  COALESCE(h003040, 0) AS h003040,
  COALESCE(cuo.r001003, 'No Def.') AS wh003040,
  h003041,
  h003042,
  h003043,
  h003044,
  COALESCE(con.r001003, 'No Def.') AS wh003044,
  h003045,
  h003046,
  h003047,
  h003048,
  h003049
FROM ilh003
LEFT JOIN ilm004 ON h003008 = m004001
LEFT JOIN ilr001 can ON can.r001001 = 1 AND can.r001002 <> ' ' AND can.r001002 = h003002
LEFT JOIN ilm002 mon ON mon.m002001 = h003003
LEFT JOIN ilr001 gra ON gra.r001001 = 6 AND gra.r001002 <> ' ' AND gra.r001002 = m004003
LEFT JOIN ilr001 acc ON acc.r001001 = 7 AND acc.r001002 <> ' ' AND acc.r001002 = m004004
LEFT JOIN ilr001 txn ON txn.r001001 = 14 AND txn.r001002 <> ' ' AND txn.r001002 = LPAD(h003023::text, 4, '0')
LEFT JOIN ilr001 res ON res.r001001 = 17 AND res.r001002 <> ' ' AND res.r001002 = LPAD(h003025::text, 4, '0')
LEFT JOIN ilr001 ent ON ent.r001001 = 15 AND ent.r001002 <> ' ' AND ent.r001002 = h003028
LEFT JOIN ilr001 ges ON ges.r001001 = 13 AND ges.r001002 <> ' ' AND ges.r001002 = h003022
LEFT JOIN ilr001 rie ON rie.r001001 = 21 AND rie.r001002 <> ' ' AND rie.r001002 = h003038
LEFT JOIN ilr001 cuo ON cuo.r001001 = 20 AND cuo.r001002 <> ' ' AND cuo.r001002 = LPAD(h003040::text, 3, '0')
LEFT JOIN ilr001 nod ON nod.r001001 = 18 AND nod.r001002 <> ' ' AND nod.r001002 = h003026
LEFT JOIN ilr001 tip ON tip.r001001 = 19 AND tip.r001002 <> ' ' AND tip.r001002 = h003017
LEFT JOIN ilr001 tpr ON tpr.r001001 = 22 AND tpr.r001002 <> ' ' AND tpr.r001002 = LPAD(h003039::text, 3, '0')
LEFT JOIN ilr001 con ON con.r001001 = 23 AND con.r001002 <> ' ' AND con.r001002 = h003044;
  
CREATE OR REPLACE VIEW ilh005v0 (
    h005v001,
    h005v002,
    h005v003,
    h005v004,
    h005v005,
    h005v006,
    h005v007,
    h005v008
) AS
SELECT 
    h005001,
    h005002,
    h005003,
    CASE 
        WHEN h005005 < 7 THEN '1'
        WHEN h005005 < 13 THEN '2'
        WHEN h005005 < 19 THEN '3'
        ELSE '4'
    END AS h005v004,
    h005004,
    SUM(h005006) AS h005v006,
    SUM(h005007) AS h005v007,
    SUM(h005009) AS h005v008
FROM ilh005
WHERE h005001 <> ''
  AND h005002 <> ''
  AND h005003 <> ''
  AND h005006 > 0
  AND h005012 = ' '
GROUP BY 
    h005001,
    h005002,
    h005003,
    h005005,
    h005004;
  
CREATE OR REPLACE VIEW ilh005v1 (
    h005v101,
    h005v102,
    h005v103,
    h005v104,
    h005v105,
    h005v106,
    h005v107,
    h005v108
) AS
SELECT 
    h005001,
    h005002,
    h005003,
    CASE 
        WHEN h005005 < 7 THEN '1'
        WHEN h005005 < 13 THEN '2'
        WHEN h005005 < 19 THEN '3'
        ELSE '4'
    END AS h005v104,
    h005004,
    SUM(h005006) AS h005v106,
    SUM(h005007) AS h005v107,
    SUM(h005009) AS h005v108
FROM ilh005
WHERE h005001 <> ''
  AND h005002 <> ''
  AND h005003 <> ''
  AND h005006 > 0
  AND h005012 = 'F'
GROUP BY 
    h005001,
    h005002,
    h005003,
    h005005,
    h005004;
  
CREATE OR REPLACE VIEW ilh006v0 (
    h006v001,
    h006v002,
    h006v003,
    h006v004,
    h006v005,
    h006v006,
    h006v007,
    h006v008
) AS
SELECT 
    h006001,
    h006002,
    h006003,
    CASE 
        WHEN h006005 < 7 THEN '1'
        WHEN h006005 < 13 THEN '2'
        WHEN h006005 < 19 THEN '3'
        ELSE '4'
    END AS h006v004,
    h006004,
    SUM(h006006) AS h006v006,
    SUM(h006007) AS h006v007,
    SUM(h006009) AS h006v008
FROM ilh006
WHERE h006001 <> 0
  AND h006002 <> ''
  AND h006003 <> ''
  AND h006007 > 0
  AND h006012 = ' '
GROUP BY 
    h006001,
    h006002,
    h006003,
    h006005,
    h006004;
  
CREATE OR REPLACE VIEW ilh006v1 (
    h006v101,
    h006v102,
    h006v103,
    h006v104,
    h006v105,
    h006v106,
    h006v107,
    h006v108
) AS
SELECT 
    h006001,
    h006002,
    h006003,
    CASE 
        WHEN h006005 < 7 THEN '1'
        WHEN h006005 < 13 THEN '2'
        WHEN h006005 < 19 THEN '3'
        ELSE '4'
    END AS h006v104,
    h006004,
    SUM(h006006) AS h006v106,
    SUM(h006007) AS h006v107,
    SUM(h006009) AS h006v108
FROM ilh006
WHERE h006001 <> 0
  AND h006002 <> ''
  AND h006003 <> ''
  AND h006007 > 0
  AND h006012 = 'F'
GROUP BY 
    h006001,
    h006002,
    h006003,
    h006005,
    h006004;

CREATE OR REPLACE VIEW ilh008v0 (
    codcli,
    totcli
) AS
SELECT 
    h008002 AS codcli,
    SUM(h008004) AS totcli
FROM ilh008
WHERE h008005 = '0'
GROUP BY h008002;
  
CREATE OR REPLACE VIEW ilh008v1 (
    codcli,
    codtxn,
    total
) AS
SELECT 
    h008002 AS codcli,
    h008003 AS codtxn,
    SUM(h008004) AS total
FROM ilh008
WHERE h008005 = '0'
GROUP BY h008002, h008003;
  
CREATE OR REPLACE VIEW ilm006v0 (
    m006001,
    m006002,
    m006003,
    m006004,
    dsc_m006004,
    m006023,
    dsc_m006023,
    m006025,
    m006026,
    m006028,
    m006029,
    dsc_unidad,
    m006031,
    dsc_m006031,
    m006033,
    m006035,
    m006037,
    m006039,
    dsc_m006039,
    m006040,
    dsc_m006040,
    m006041,
    m006042,
    m006044,
    m006045,
    m006047,
    m006048,
    m006050
) AS
SELECT
    m006001,
    m006002,
    m006003,
    m006004,
    CASE
        WHEN m006004 = 'RR' THEN 'Financiero'
        WHEN m006004 = '00' THEN 'Canales'
        ELSE 'No. Def.'
    END AS dsc_m006004,
    
    m006023,
    CASE
        WHEN m006023 = 'N' THEN 'Persona Natural'
        WHEN m006023 = 'J' THEN 'Persona Juridica'
        WHEN m006023 = 'G' THEN 'Gobierno'
        ELSE 'No. Def.'
    END AS dsc_m006023,

    m006025,
    m006026,
    m006028,
    m006029,
    CASE
        WHEN m006029 = 'H' THEN 'Horas'
        WHEN m006029 = 'M' THEN 'Minutos'
        WHEN m006029 = 'S' THEN 'Segundos'
        ELSE 'No. Def.'
    END AS dsc_unidad,

    m006031,
    COALESCE(res.r001003, 'No Def.') AS dsc_m006031,
    m006033,
    m006035,
    m006037,
    m006039,
    COALESCE(ale.m004002, 'No Def.') AS dsc_m006039,
    m006040,
    CASE
        WHEN m006040 = '0' THEN 'Activo'
        WHEN m006040 = '1' THEN 'Suspendido'
        WHEN m006040 = '9' THEN 'Desactivada'
        ELSE 'No. Def.'
    END AS dsc_m006040,

    m006041,
    m006042,
    m006044,
    m006045,
    m006047,
    m006048,
    m006050
FROM ilm006
LEFT JOIN ilm004 ale
    ON ale.m004001 = m006039
LEFT JOIN ilr001 res
    ON res.r001001 = 17
   AND res.r001002 <> ' '
   AND res.r001002 = m006031;
  
CREATE OR REPLACE VIEW ilm015v0 (
    num_item,
    descrip,
    identif,
    intrum,
    codcomer,
    terminal,
    origen,
    dsc_orig,
    pais,
    dsc_pais,
    canal,
    dsc_canal,
    moneda,
    dsc_mon,
    cod_tra,
    dsc_tra,
    t_per,
    dsc_per,
    cat_com,
    dsc_cate,
    mto_tra,
    estatus,
    dsc_sts,
    usuario,
    fechora
) AS
SELECT
    m015001 AS num_item,
    m015002 AS descrip,
    m015003 AS identif,
    m015004 AS intrum,
    m015005 AS codcomer,
    m015006 AS terminal,
    m015007 AS origen,
    CASE
        WHEN m015007 = 'RR' THEN 'Financiero'
        WHEN m015007 = '00' THEN 'Canales'
        ELSE 'No Definido'
    END AS dsc_orig,
    m015008 AS pais,
    COALESCE(pai.r001003, 'No Def.') AS dsc_pais,
    m015009 AS canal,
    COALESCE(can.r001003, 'No Def.') AS dsc_canal,
    m015010 AS moneda,
    COALESCE(mon.m002002, 'No Def.') AS dsc_mon,
    m015011 AS cod_tra,
    COALESCE(tra.r001003, 'No Def.') AS dsc_tra,
    m015012 AS t_per,
    CASE
        WHEN m015012 = 'N' THEN 'Persona Natural'
        WHEN m015012 = 'J' THEN 'Persona Juridica'
        WHEN m015012 = 'G' THEN 'Gobierno'
        ELSE 'No Definido'
    END AS dsc_per,
    m015013 AS cat_com,
    COALESCE(cat.r001003, 'No Def.') AS dsc_cate,
    m015014 AS mto_tra,
    m015015 AS estatus,
    CASE
        WHEN m015015 = '0' THEN 'Activo'
        WHEN m015015 = '1' THEN 'Suspendido'
        WHEN m015015 = '9' THEN 'Desactivada'
        ELSE 'No Definido'
    END AS dsc_sts,
    m015016 AS usuario,
    m015017 AS fechora
FROM ilm015
LEFT JOIN ilr001 pai 
  ON pai.r001001 = 3 AND pai.r001002 <> ' ' AND pai.r001002 = m015008
LEFT JOIN ilr001 cat 
  ON cat.r001001 = 12 AND cat.r001002 <> ' ' AND cat.r001002 = m015013
LEFT JOIN ilr001 can 
  ON can.r001001 = 1 AND can.r001002 <> ' ' AND can.r001002 = m015009
LEFT JOIN ilm002 mon 
  ON mon.m002001 = m015010
LEFT JOIN ilr001 tra 
  ON tra.r001001 = 14 AND tra.r001002 <> ' ' AND tra.r001002 = Dec(m015011, 3, 0);
  
CREATE OR REPLACE VIEW ilw001v0 (
    w001v001,
    w001v002,
    w001v003,
    w001v004,
    w001v005,
    w001v006,
    w001v007,
    w001v008,
    w001v009,
    w001v010,
    w001v011,
    w001v012,
    w001v013
) AS
SELECT 
    w001001,
    w001002,
    w001003,
    w001004,
    TO_DATE(w001005 || '-' || w001006 || '-' || w001007, 'YYYY-MM-DD') AS w001v005,
    w001008,
    w001009,
    w001010,
    w001011,
    w001012,
    w001013,
    w001014,
    w001015
FROM ilw001;

  
   

  
