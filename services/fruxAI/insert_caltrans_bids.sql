-- Caltrans Bids INSERT komutları
-- Tablo adı: caltrans_bids (varsayılan)

INSERT INTO caltrans_bids (contract_number, number_of_bidders, bid_rank, bid_amount, bidder_id) VALUES
('10-1L8604', 6, 1, 2053700.00, 'VC1200002736'),
('10-1L8604', 6, 2, 2271255.20, 'VC1500004960'),
('10-1L8604', 6, 3, 2287000.00, 'VC2000002246'),
('10-1L8604', 6, 4, 2307077.55, 'VC1700000908'),
('10-1L8604', 6, 5, 2324503.15, 'VC2200003483'),
('10-1L8604', 6, 6, 2575075.00, 'VC1200003869');

-- INSERT sonrası kontrol
SELECT COUNT(*) as total_records FROM caltrans_bids;
SELECT * FROM caltrans_bids ORDER BY bid_rank;
