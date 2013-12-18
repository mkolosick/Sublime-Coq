(* Exercise: 1 star (nandb) *)
Definition nandb (b1 : bool) (b2 : bool) : bool :=
  match b1 with
    | false => true
    | true => negb b2
  end.

Example test_nandb1: (nandb true false) = true.
Proof. reflexivity. Qed.
Example test_nandb2: (nandb false false) = true.
Proof. reflexivity. Qed.
Example test_nandb3: (nandb false true) = true.
Proof. reflexivity. Qed.
Example test_nandb4: (nandb true true) = false.
Proof. reflexivity. Qed.

(* Exercise: 1 star (andb3) *)
Definition andb3 (b1 : bool) (b2 : bool) (b3 : bool) : bool :=
  match b1 with
    | true => match b2 with
                | true => b3
                | false => false
              end
    | false => false
  end.

Example test_andb31: (andb3 true true true) = true.
Proof. reflexivity. Qed.
Example test_andb32: (andb3 false true true) = false.
Proof. reflexivity. Qed.
Example test_andb33: (andb3 true false true) = false.
Proof. reflexivity. Qed.
Example test_andb34: (andb3 true true false) = false.
Proof. reflexivity. Qed.

(* Exercise: 1 star (factorial) *)
Fixpoint factorial (n : nat) : nat :=
  match n with
    | 0 => 1
    | S n' => (S n') * (factorial n')
  end.

Example test_factorial1: (factorial 3) = 6.
Proof. reflexivity. Qed.
Example test_factorial2: (factorial 5) = (mult 10 12).
Proof. reflexivity. Qed.

(* Exercise: 2 star (blt_nat) *)
Fixpoint ble_nat (n m : nat) : bool :=
  match n with
    | 0 =>  true
    | S n' =>  match m with
                | 0 => false
                | S m' => ble_nat n' m'
              end
  end.

Example test_ble_nat1: (ble_nat 2 2) = true.
Proof. reflexivity. Qed.
Example test_ble_nat2: (ble_nat 2 4) = true.
Proof. reflexivity. Qed.
Example test_ble_nat3: (ble_nat 4 2) = false.
Proof. reflexivity. Qed.

Definition blt_nat (n m : nat) : bool := ble_nat (n + 1) m.

Example test_blt_nat1: (blt_nat 2 2) = false.
Proof. reflexivity. Qed.
Example test_blt_nat2: (blt_nat 2 4) = true.
Proof. reflexivity. Qed.
Example test_blt_nat3: (blt_nat 4 2) = false.
Proof. reflexivity. Qed.

(* Exercise: 1 star (plus_id_exercise) *)
Theorem plus_id_exercise:
  forall n m o : nat,
  n = m -> m = o -> n + m = m + o.
Proof.
  intros n m o.
  intros H1.
  intros H2.
  rewrite -> H1.
  rewrite <- H2.
  reflexivity.
Qed.

(* Exercise: 2 stars (mult_S_1) *)
Theorem mult_S_1:
  forall n m : nat,
  m = S n ->
  m * (1 + n) = m * m.
Proof.
  intros n m.
  intros H.
  simpl.
  rewrite <- H.
  reflexivity.
Qed.

(* Exercise: 1 star (zero_nbeq_plus_1) *)
Fixpoint beq_nat (n m : nat) : bool :=
  match n with
  | 0 => match m with
         | 0 => true
         | S m' => false
         end
  | S n' => match m with
            | 0 => false
            | S m' => beq_nat n' m'
            end
  end.

Theorem zero_nbeq_plus_1 :
  forall n : nat,
  beq_nat 0 (n + 1) = false.
Proof.
  intros n. destruct n as [| n'].
  (* CASE n = 0 *)
    simpl. reflexivity.
  (* CASE n = S n' *)
    simpl. reflexivity.
Qed.

(* Exercise: 2 stars (boolean functions) *)
Theorem identity_fn_applied_twice :
  forall (f : bool -> bool),
  (forall (x : bool), f x = x) ->
  forall (b : bool), f (f b) = b.
Proof.
  intros f.
  intros H.
  intros b.
  rewrite -> H.
  rewrite -> H.
  reflexivity.
Qed.

(* Exercise: 2 stars (andb_eq_orb) *)
Lemma andb_t_f : andb true false = false.
Proof. reflexivity. Qed.

Lemma andb_f_t : andb false true = false.
Proof. reflexivity. Qed.

Theorem andb_eq_orb :
  forall (b c : bool),
  (andb b c = orb b c) -> b = c.
Proof.
  intros b c H. destruct b.
  (* CASE b = true *)
    destruct c.
    (* CASE c = true *)
      reflexivity.
    (* CASE c = false *)
      rewrite <- andb_t_f.
      rewrite H.
      reflexivity.
  (* CASE b = false *)
    destruct c.
    (* CASE c = true *)
      rewrite <- andb_f_t.
      rewrite H.
      reflexivity.
    (* CASE C = false *)
      reflexivity.
Qed.

(* Exercise: 3 stars (binary) *)
Inductive bin : Type := 
  | O : bin
  | twice : bin -> bin
  | one_more_twice : bin -> bin.

Fixpoint add1_bin (b : bin) : bin :=
  match b with
    | O => one_more_twice O
    | twice b' => one_more_twice b'
    | one_more_twice b' => twice (add1_bin b')
  end.

Fixpoint bin_to_nat (b : bin) : nat :=
  match b with
    | O => 0
    | twice b' => 2 * (bin_to_nat b')
    | one_more_twice b' => S (2 * (bin_to_nat b'))
  end.

Example test_add1_bin0 : bin_to_nat (add1_bin O) = S (bin_to_nat O).
Proof. reflexivity. Qed.
Example test_add1_bin1 : bin_to_nat (add1_bin (one_more_twice O)) = S (bin_to_nat (one_more_twice O)).
Proof. reflexivity. Qed.
Example test_add1_bin5 : bin_to_nat (add1_bin (one_more_twice (twice (one_more_twice O)))) =
  S (bin_to_nat (one_more_twice (twice (one_more_twice O)))).
Proof. reflexivity. Qed.

(* Exercise: 2 stars, optional (decreasing) *)
(*
Fixpoint terminating_but_unacceptable (x : nat) : nat :=
  match x with
    | 0 => 0
    | S x' => terminating_but_unacceptable ((x' * 2) - (x' * 3))
  end.
*)