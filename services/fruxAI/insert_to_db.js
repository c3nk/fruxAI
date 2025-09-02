// Node.js ile PostgreSQL'e veri ekleme script'i
const { Client } = require('pg');

const client = new Client({
  host: 'fruxai-db',
  port: 5432,
  user: 'postgres',
  password: 'fruxai_password',
  database: 'fruxai'
});

async function insertCaltransBids() {
  try {
    await client.connect();
    console.log('✅ PostgreSQL bağlantısı başarılı');

    // Tablo oluştur (eğer yoksa)
    await client.query(`
      CREATE TABLE IF NOT EXISTS caltrans_bids (
        id SERIAL PRIMARY KEY,
        contract_number VARCHAR(50),
        number_of_bidders INTEGER,
        bid_rank INTEGER,
        bid_amount DECIMAL(15,2),
        bidder_id VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    console.log('✅ Tablo hazır');

    // Verileri ekle
    const bids = [
      ['10-1L8604', 6, 1, 2053700.00, 'VC1200002736'],
      ['10-1L8604', 6, 2, 2271255.20, 'VC1500004960'],
      ['10-1L8604', 6, 3, 2287000.00, 'VC2000002246'],
      ['10-1L8604', 6, 4, 2307077.55, 'VC1700000908'],
      ['10-1L8604', 6, 5, 2324503.15, 'VC2200003483'],
      ['10-1L8604', 6, 6, 2575075.00, 'VC1200003869']
    ];

    for (const bid of bids) {
      await client.query(
        'INSERT INTO caltrans_bids (contract_number, number_of_bidders, bid_rank, bid_amount, bidder_id) VALUES ($1, $2, $3, $4, $5)',
        bid
      );
    }

    console.log('✅ 6 kayıt başarıyla eklendi');

    // Kontrol
    const result = await client.query('SELECT COUNT(*) as total FROM caltrans_bids');
    console.log('📊 Toplam kayıt sayısı:', result.rows[0].total);

  } catch (err) {
    console.error('❌ Hata:', err.message);
  } finally {
    await client.end();
    console.log('🔌 Bağlantı kapatıldı');
  }
}

insertCaltransBids();
