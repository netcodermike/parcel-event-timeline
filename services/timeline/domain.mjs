export async function operation({ parcel, scans }, log) {
  const { history } = await log({ parcel, scans })
  const sequence = history.map(scan => scan.status)
  return { parcel, events: history.length, current: sequence.at(-1) ?? 'unknown', sequence, history }
}
