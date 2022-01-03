#include "soidlib.h"

int main( int argc, char** argv ) {

  // intercept,seasonSPRING,seasonSUMMER,seasonFALL,holiday,workingday,weathersitMISTY,weathersitRAIN/SNOW/SNOWSTORM,temp,hum,windspeed,days_since_2011
  double model[ 12 ] = { 2399.4f, 899.3f, 138.2f, 425.6f, -686.1f, 124.9f, -379.4f, -1901.5f, 110.7f, -17.4f, -42.5f, 4.9f };

  // instant,dteday,season,yr,mnth,holiday,weekday,workingday,weathersit,temp,atemp,hum,windspeed,casual,registered,cnt
  // 6,2011-01-06,1,0,1,0,4,1,1,0.204348,0.233209,0.518261,0.0895652,88,1518,1606
  //double instance[ 12 ] = { 1.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f, 0.0f, 0.0f, 1.604346f, 51.8261f, 6.000868f, 5.0f };

  double instance[ 12 ];

  klee_make_symbolic( &instance, sizeof( instance ), "instance" );

  klee_assume( instance[ 0 ] == 1.0f ); // intercept
  klee_assume( instance[ 1 ] == 0.0f ); // spring
  klee_assume( instance[ 2 ] == 0.0f ); // summer
  klee_assume( instance[ 3 ] == 0.0f ); // fall
  klee_assume( instance[ 4 ] == 0.0f ); // holiday
  klee_assume( instance[ 5 ] == 1.0f ); // workingday
  klee_assume( instance[ 6 ] == 0.0f ); // misty
  klee_assume( instance[ 7 ] == 0.0f ); // rain/snow
  //klee_assume( instance[ 8 ] == 1.604346f ); // temperature
  klee_assume( -3.88889 <= instance[ 8 ] && instance[ 8 ] <= 10.0f  ); // temperature
  klee_assume( instance[ 9 ] == 51.8261f ); // humidity
  //klee_assume( instance[ 10 ] == 6.000868f ); // windspeed
  klee_assume( 0.0f <= instance[ 10 ] && instance[ 10 ] <= 10.0f ); // windspeed
  klee_assume( instance[ 11 ] == 5.0f );

  double proj = 0.0f;

  double __soid__proj;
  klee_make_symbolic( &__soid__proj, sizeof( __soid__proj ), "__soid__proj" );

  for ( int i = 0; i < 12; i++ ) proj += model[ i ] * instance[ i ];

  klee_assume( proj == __soid__proj );

  return 0;
}
