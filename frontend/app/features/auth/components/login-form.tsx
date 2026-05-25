import { Link, useNavigate } from 'react-router';
import { type FormEvent, useState } from 'react';
import { useAuthStore } from '~/features/auth/auth.store';

export default function LoginForm() {
  const navigate = useNavigate();
  const [hover, setHover] = useState(false);
  const { login, hydrateUser, isLoading } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    try {
      await login({ email, password });
      navigate('/');
    } catch (err) {
      console.log('Login failed', err);
    }
  }

  return (
    <form className='form' onSubmit={handleSubmit}>
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
        {isLoading ? 'Loading...' : 'login'}
      </button>

      <p style={{ color: 'grey', fontSize: 12 }}>
        don't have an account?{' '}
        <Link to="/auth/register" style={{ color: 'white' }}>
          <u>register here</u>
        </Link>
      </p>
    </form>
  );
}


