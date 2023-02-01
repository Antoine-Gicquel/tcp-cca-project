#include <net/tcp.h>


static u32 max_cwnd = 0x00007fff;

static void infinitytcp_init(struct sock *sk)
{
	struct tcp_sock *tp = tcp_sk(sk);
	tcp_snd_cwnd_set(tp, max_cwnd);
}

static u32 infinitytcp_recalc_ssthresh(struct sock *sk)
{
	struct tcp_sock *tp = tcp_sk(sk);
	tcp_snd_cwnd_set(tp, max_cwnd);
	return max_cwnd;
}

static void infinitytcp_cong_avoid(struct sock *sk, u32 ack, u32 acked)
{
	struct tcp_sock *tp = tcp_sk(sk);
	tcp_snd_cwnd_set(tp, max_cwnd);
}

static void infinitytcp_state(struct sock *sk, u8 new_state)
{
	struct tcp_sock *tp = tcp_sk(sk);
	tcp_snd_cwnd_set(tp, max_cwnd);
}

static u32 infinitytcp_undo_cwnd(struct sock *sk)
{
	struct tcp_sock *tp = tcp_sk(sk);
	tcp_snd_cwnd_set(tp, max_cwnd);
	return max_cwnd;
}

static void infinitytcp_cwnd_event(struct sock *sk, enum tcp_ca_event event)
{
	struct tcp_sock *tp = tcp_sk(sk);
	tcp_snd_cwnd_set(tp, max_cwnd);
}

static void infinitytcp_acked(struct sock *sk, const struct ack_sample *sample)
{
	struct tcp_sock *tp = tcp_sk(sk);
	tcp_snd_cwnd_set(tp, max_cwnd);
}

static struct tcp_congestion_ops infinitytcp __read_mostly = {
	.init		= infinitytcp_init,
	.ssthresh	= infinitytcp_recalc_ssthresh,
	.cong_avoid	= infinitytcp_cong_avoid,
	.set_state	= infinitytcp_state,
	.undo_cwnd	= infinitytcp_undo_cwnd,
	.cwnd_event	= infinitytcp_cwnd_event,
	.pkts_acked = infinitytcp_acked,
	.owner		= THIS_MODULE,
	.name		= "infinity",
};

static int __init infinitytcp_register(void)
{
	return tcp_register_congestion_control(&infinitytcp);
}

static void __exit infinitytcp_unregister(void)
{
	tcp_unregister_congestion_control(&infinitytcp);
}

module_init(infinitytcp_register);
module_exit(infinitytcp_unregister);

MODULE_AUTHOR("Antoine GICQUEL");
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("INFINITY TCP");
MODULE_VERSION("1.0");
