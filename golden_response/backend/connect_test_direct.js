import { MongoClient } from 'mongodb';

const uri = 'mongodb://bansalyash316_db_user:Rv7ljsytxs60BjfO@ac-jdhu0ye-shard-00-00.5t2kxf7.mongodb.net:27017,ac-jdhu0ye-shard-00-01.5t2kxf7.mongodb.net:27017,ac-jdhu0ye-shard-00-02.5t2kxf7.mongodb.net:27017/expense_splitter?authSource=admin&tls=true&retryWrites=true&w=majority';
const client = new MongoClient(uri);

const run = async () => {
  try {
    await client.connect();
    console.log('direct connected');
  } catch (err) {
    console.error('direct connect failed', err);
    process.exit(1);
  } finally {
    await client.close();
  }
};

run();
