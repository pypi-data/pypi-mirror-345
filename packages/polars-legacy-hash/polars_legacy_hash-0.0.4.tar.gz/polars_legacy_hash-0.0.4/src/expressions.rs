use polars::prelude::*;
use crate::expressions::DataType::Int8;
use pyo3_polars::{derive::polars_expr};

use ahash::RandomState;

#[polars_expr(output_type=UInt64)]
fn legacy_hash(inputs: &[Series]) -> PolarsResult<Series> {
    eprintln!("test ouytput1");
    let s = inputs.get(0).expect("no series received");
    // let s = Series::new("foo", &[1, 2, 3]).cast(&Int8).unwrap();
    println!("Series name: {}, dtype: {:?}", s.name(), s.dtype());
    let rs = RandomState::with_seeds(0, 0, 0, 0);
    let mut h: Vec<u64> = vec![];
    let ser_name: &str = s.name();
    let x = s.vec_hash(rs, &mut h);
    eprintln!("test ouytput");
    eprintln!("{:?}", x);

    match x {
        Ok(_) => Ok(UInt64Chunked::from_vec(&ser_name, h).into_series()),

        Err(res) => Err(res),
    }
}


// TODO move
#[test]
fn test_hash_int8_series() {
    // let s: Series = (0..10).map(Some).collect();
    let s = Series::new("foo", &[1, 2, 3]);
    let res = s.cast(&Int8);
    let s = res.unwrap();
    // let ca: Int8Chunked = (0..10).map(Some).collect();
    // let s = ca.into_series();

    println!("test");
    println!("Series name: {}, dtype: {:?}", s.name(), s.dtype());
    // let s = PySeries::new("a", &[1_i8, 2, 3]);
    let mut h = Vec::new();
    s.vec_hash(RandomState::with_seeds(0,0,0,0), &mut h).unwrap();

    println!("hash: {:?}, ", h);
    let out = UInt64Chunked::from_vec(&s.name(), h).into_series();
    println!("out: {:?}, ", out);


}