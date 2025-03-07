PREFIX=$1

cd $PREFIX
git clone https://github.com/TwilCynder/alumet
cd alumet
git switch mojitos-build-lib
cd agent
cargo build --release
