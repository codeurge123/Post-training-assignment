import { promises as dns } from 'dns';

const run = async () => {
  try {
    const srv = await dns.resolveSrv('_mongodb._tcp.cluster0.5t2kxf7.mongodb.net');
    console.log('srv results', srv);
  } catch (err) {
    console.error('dns failed', err);
    process.exit(1);
  }
};

run();
