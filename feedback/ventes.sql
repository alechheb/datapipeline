-- 1 ere partie du test SQL:

SELECT date sum(prod_price*prod_qty) AS ventes FROM transaction
WHERE date between '2019-01-01' AND '2019-12-31'
GROUP BY date
ORDER BY date;

-- 2ème partie du test SQL:

SELECT client_id, SUM(ventes_meubles) AS ventes_meubles, SUM(ventes_deco) AS ventes_deco FROM (
    SELECT
        client_id,
        SUM(CASE WHERE product_type='MEUBLE' THEN prod_price * prod_qty ELSE 0 END) AS ventes_meubles,
        SUM(CASE WHERE product_type='DECO' THEN prod_price * prod_qty ELSE 0 END) AS ventes_deco
    FROM transaction JOIN product_nomenclature on transaction.prod_id = product_nomenclature.product_id
    WHERE date between '2019-01-01' AND '2019-12-31'
    GROUP BY client_id, product_type
) AS clients_ventes
GROUP BY client_id;
