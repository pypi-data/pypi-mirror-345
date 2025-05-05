print("""show dbs;

use test;

db.createCollection("products");


db.products.insertOne({name: 'Laptop', category: 'Electronics', price: 40000});


db.products.insertMany([
  {name: 'Smartphone', category: 'Electronics', price: 10000},
   {name: 'Books', category: 'Stationary', price: 500}
]);


db.products.find();


db.products.find({name: 'Books'});


db.products.find({price: {$lt: 20000}});



db.products.updateOne(
   {name: 'Laptop'},
   {$set: {price: 70000}}
); 



db.products.updateMany(
   {category: 'Electronics'},
   {$set: {category: 'Tech Gadgets'}}
); 


db.products.deleteOne({name: 'Laptop'});


db.products.deleteMany({ category: 'Electronics' });""")


