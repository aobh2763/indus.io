import { Link, useNavigate } from 'react-router';
import { type FormEvent, useState } from 'react';
import { useAuthStore } from '~/features/auth/auth.store';

export default function RegisterForm() {
  const navigate = useNavigate();
  const [hover, setHover] = useState(false);
  const { register, isLoading } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [lastName, setLastName] = useState('');
  const [firstName, setFirstName] = useState('');

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    try {
      await register({
        firstName,
        lastName,
        email,
        password,
      });

      navigate('/auth/login');
    } catch (err) {
      console.error('Register failed', err);
    }
  }

  return (
    <form className='form' onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="first name"
        value={firstName}
        onChange={(e) => setFirstName(e.target.value)}
      />

      <input
        type="text"
        placeholder="last name"
        value={lastName}
        onChange={(e) => setLastName(e.target.value)}
      />

      <input
        type="email"
        placeholder="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <input
        type="password"
        placeholder="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button
        type="submit"
        disabled={isLoading}
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
        style={{
          opacity: isLoading ? 0.5 : 1,
          backgroundColor: hover ? 'white' : 'black',
          color: hover ? 'black' : 'white',
        }}
      >
        {isLoading ? 'Loading...' : 'register'}
      </button>

      <p style={{ color: 'grey', fontSize: 12 }}>
        already have an account?{' '}
        <Link to="/auth/login" style={{ color: 'white' }}>
          <u>login here</u>
        </Link>
      </p>
    </form>
  );
}
