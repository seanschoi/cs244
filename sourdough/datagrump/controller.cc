#include <iostream>

#include "controller.hh"
#include "timestamp.hh"

#define ALG 2

using namespace std;

/* Default constructor */
Controller::Controller( const bool debug )
  : debug_( debug )
{}

// Start with the best window size that we found
unsigned int window_size_val = 13;

/* Get current window size, in datagrams */
unsigned int Controller::window_size( void )
{
  /* Default: fixed window size of 100 outstanding datagrams */
  // UNUSED NOW
  //unsigned int the_window_size = 13;

  if ( debug_ ) {
    cerr << "At time " << timestamp_ms()
	 << " window size is " << window_size_val << endl;
  }

  return window_size_val;
}

/* A datagram was sent */
void Controller::datagram_was_sent( const uint64_t sequence_number,
				    /* of the sent datagram */
				    const uint64_t send_timestamp )
                                    /* in milliseconds */
{
  /* Default: take no action */

  if ( debug_ ) {
    cerr << "At time " << send_timestamp
	 << " sent datagram " << sequence_number << endl;
  }
}

/* An ack was received */
void Controller::ack_received( const uint64_t sequence_number_acked,
			       /* what sequence number was acknowledged */
			       const uint64_t send_timestamp_acked,
			       /* when the acknowledged datagram was sent (sender's clock) */
			       const uint64_t recv_timestamp_acked,
			       /* when the acknowledged datagram was received (receiver's clock)*/
			       const uint64_t timestamp_ack_received )
                               /* when the ack was received (by sender) */
{
  /* Default: take no action */

  if ( debug_ ) {
    cerr << "At time " << timestamp_ack_received
	 << " received ack for datagram " << sequence_number_acked
	 << " (send @ time " << send_timestamp_acked
	 << ", received @ time " << recv_timestamp_acked << " by receiver's clock)"
    << " yo " << recv_timestamp_acked - send_timestamp_acked
	 << endl;
  }
#if ALG == 1
    // Simple AIMD
    //shouldn't this be somwhere else? because this should happen unrelated to RTT or if the packet was recived no? because right now it's really similar to trig
    if (timestamp_ack_received - send_timestamp_acked < timeout_ms()) {
        window_size_val += 1;
    }
    else {
        window_size_val /= 2;
        if (window_size_val == 0) {
            window_size_val = 1;
        }
    }
#elif ALG == 2 //essentially TIMELY with lambda = beta = 1 and no gradiant (Should I add?) (so not TIMELY)
    //delay triggered
    double rtt = timestamp_ack_received - send_timestamp_acked;
    //taken from TIMELY 
    double t_low = 0.05; //50 micro-secs
    double t_high = 0.5; //500 micro-secs
    if (rtt < t_low) {
       window_size_val += 1;
    }
    else if (rtt > t_high) {
    	window_size_val *= t_high / rtt;
        if (window_size_val == 0) {
            window_size_val = 1;
        } 
    } //else keep unchanged unless we decide on the gradiant thing
#endif 
}

/* How long to wait (in milliseconds) if there are no acks
   before sending one more datagram */
unsigned int Controller::timeout_ms( void )
{
  return 70; /* timeout of 70 millisecond */
}
