import { MongoClient } from 'mongodb';

const uri = 'mongodb+srv://bansalyash316_db_user:Rv7ljsytxs60BjfO@cluster0.5t2kxf7.mongodb.net/expense_splitter?retryWrites=true&w=majority';
const client = new MongoClient(uri);

const run = async () => {
  try {
    await client.connect();
    console.log('connected');
  } catch (err) {
    console.error('connect failed', err);
    process.exit(1);
  } finally {
    await client.close();
  }
};

run();
