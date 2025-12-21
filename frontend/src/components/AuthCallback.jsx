import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

export default function AuthCallback({ onSuccess }) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const token = searchParams.get('token');

    if (token) {
      localStorage.setItem('token', token);
      onSuccess();
      navigate('/chat');
    } else {
      console.error('No token found in callback');
      navigate('/');
    }
  }, [searchParams, navigate, onSuccess]);

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="text-white text-xl">Logging in...</div>
    </div>
  );
}
