import { SQLiteDBConnection } from '@capacitor-community/sqlite';

export const handleBreeding = async (method: string, pathParts: string[], payload: any, db: SQLiteDBConnection) => {
  const resource = pathParts[0]; // pairings, clutches, chicks, breeding
  const id = pathParts.length > 1 ? pathParts[1] : null;

  if (resource === 'breeding' && pathParts[1] === 'analytics') {
    const totalPairingsRes = await db.query('SELECT COUNT(*) as count FROM pairing');
    const totalPairings = totalPairingsRes.values?.[0]?.count || 0;

    const totalClutchesRes = await db.query('SELECT COUNT(*) as count FROM clutch');
    const totalClutches = totalClutchesRes.values?.[0]?.count || 0;

    const eggsRes = await db.query('SELECT SUM(total_eggs) as total, SUM(hatched_eggs) as hatched, SUM(fertile_eggs) as fertile FROM clutch');
    const totalEggs = eggsRes.values?.[0]?.total || 0;
    const totalHatched = eggsRes.values?.[0]?.hatched || 0;

    const chicksRes = await db.query(`
      SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'fledged' THEN 1 ELSE 0 END) as fledged,
        SUM(CASE WHEN status = 'added_to_stock' THEN 1 ELSE 0 END) as promoted,
        SUM(CASE WHEN status = 'deceased' THEN 1 ELSE 0 END) as deceased
      FROM chick
    `);
    const chicksStats = chicksRes.values?.[0] || {};

    return {
      total_pairings: totalPairings,
      total_clutches: totalClutches,
      total_eggs: totalEggs,
      total_chicks_hatched: totalHatched,
      total_chicks_fledged: chicksStats.fledged || 0,
      total_promoted_to_stock: chicksStats.promoted || 0,
      total_deceased: chicksStats.deceased || 0,
      best_pairs: []
    };
  }

  if (resource === 'pairings') {
    if (method === 'GET') {
      if (id) {
        const res = await db.query('SELECT * FROM pairing WHERE id = ?', [id]);
        const pairing = res.values?.[0];
        if (pairing) {
          const clutchesRes = await db.query('SELECT * FROM clutch WHERE pairing_id = ?', [id]);
          pairing.clutches = clutchesRes.values || [];
          for (const clutch of pairing.clutches) {
            const chicksRes = await db.query('SELECT * FROM chick WHERE clutch_id = ?', [clutch.id]);
            clutch.chicks = chicksRes.values || [];
          }
        }
        return pairing || null;
      } else {
        const res = await db.query('SELECT * FROM pairing');
        return res.values || [];
      }
    } else if (method === 'POST') {
      const res = await db.run(
        'INSERT INTO pairing (bird_a_id, bird_b_id, cage_number, notes) VALUES (?, ?, ?, ?)',
        [payload.bird_a_id, payload.bird_b_id, payload.cage_number, payload.notes]
      );
      const newPairing = await db.query('SELECT * FROM pairing WHERE id = ?', [res.changes?.lastId]);
      return newPairing.values?.[0] || null;
    } else if (method === 'PUT' && id) {
      await db.run('UPDATE pairing SET end_date = ?, cage_number = ?, notes = ? WHERE id = ?', 
        [payload.end_date, payload.cage_number, payload.notes, id]);
      const updated = await db.query('SELECT * FROM pairing WHERE id = ?', [id]);
      return updated.values?.[0] || null;
    }
  } else if (resource === 'clutches') {
    if (method === 'POST') {
      const res = await db.run(
        'INSERT INTO clutch (pairing_id, clutch_date, total_eggs, fertile_eggs, hatched_eggs, eggs_lost, loss_reason, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        [payload.pairing_id, payload.clutch_date, payload.total_eggs, payload.fertile_eggs, payload.hatched_eggs, payload.eggs_lost, payload.loss_reason, payload.notes]
      );
      const newClutch = await db.query('SELECT * FROM clutch WHERE id = ?', [res.changes?.lastId]);
      return newClutch.values?.[0] || null;
    } else if (method === 'PUT' && id) {
      await db.run(
        'UPDATE clutch SET clutch_date = ?, total_eggs = ?, fertile_eggs = ?, hatched_eggs = ?, eggs_lost = ?, loss_reason = ?, notes = ? WHERE id = ?',
        [payload.clutch_date, payload.total_eggs, payload.fertile_eggs, payload.hatched_eggs, payload.eggs_lost, payload.loss_reason, payload.notes, id]
      );
      const updated = await db.query('SELECT * FROM clutch WHERE id = ?', [id]);
      return updated.values?.[0] || null;
    }
  } else if (resource === 'chicks') {
    if (method === 'POST') {
      const res = await db.run(
        'INSERT INTO chick (clutch_id, ring_id, mutation, sex, hatch_date) VALUES (?, ?, ?, ?, ?)',
        [payload.clutch_id, payload.ring_id, payload.mutation, payload.sex, payload.hatch_date]
      );
      const newChick = await db.query('SELECT * FROM chick WHERE id = ?', [res.changes?.lastId]);
      return newChick.values?.[0] || null;
    } else if (method === 'PUT' && id) {
      await db.run(
        'UPDATE chick SET status = ?, mortality_reason = ?, fledge_date = ?, ring_id = ?, mutation = ?, sex = ?, hatch_date = ? WHERE id = ?',
        [payload.status, payload.mortality_reason, payload.fledge_date, payload.ring_id, payload.mutation, payload.sex, payload.hatch_date, id]
      );
      const updated = await db.query('SELECT * FROM chick WHERE id = ?', [id]);
      return updated.values?.[0] || null;
    }
  }

  return null;
};
